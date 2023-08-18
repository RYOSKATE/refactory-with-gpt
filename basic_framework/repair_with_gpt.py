from __future__ import annotations
from typing import Optional
from basic_framework.core_testing import Tester
from basic_framework.distance import zss_multi_func_code_distance
import time
import openai
import json
import hashlib
import os
import re
import sys
from mistletoe import Document
from mistletoe.block_token import CodeFence

from basic_framework.utils import regularize, syntax_check

openai.organization = ''
openai.api_key = os.getenv("OPENAI_API_KEY")

# 実装参考:https://zenn.dev/ryo_kawamata/articles/b39ba0452fec81


def repair_code_by_gpt_with_retry(bug_code: str, description: str, sample_correct_code_blocks: list[str], gpt_model="gpt-3.5-turbo", max_retry_count=3, tester: Optional[Tester]=None) -> Optional[str]:
    init_prompt = prompt = f'''
As a Python programming expert, your objective is to correct the incorrect code provided. Follow these guidelines:
    
- Ensure your corrected code produces the same output and logic as the provided model solution.
- Make only essential modifications to the incorrect code, preserving its essence.
- Start by listing all user-defined identifiers in the incorrect code. Use as many of these identifiers as possible in your corrected code.
- Your correct code's semantics should mirror the model solution.
- Ensure the syntax of the corrected code closely resembles the incorrect original, more so than the model solution.
- Retain variable and function names, comments, whitespaces, line break characters, parentheses, `pass`, `break`, `continue`, and any redundant expressions like `list([])`.
- Avoid changing the names of user-defined identifiers from the incorrect original.
- Avoid deleting whitespaces, line breaks, parentheses, `pass`, `break`, `continue`, or any superfluous statements and function calls.

# Incorrect Code
```python
{remove_redundant_spaces(bug_code)}
```

# Model Solution
{remove_redundant_spaces(sample_correct_code_blocks[0])}

# Output Format
"""
User-defined identifiers from the incorrect code:
- <identifier>

Corrected code employing the listed identifiers:
```python
...
```
"""
    '''.strip()

    min_patch_size = sys.maxsize
    for reference_code in sample_correct_code_blocks:
        min_patch_size = min(min_patch_size, zss_multi_func_code_distance(bug_code, reference_code))

    retry_count = 0
    extra_messages = []
    while retry_count < max_retry_count:
        try:
            generated_text = _repair_code_by_gpt(prompt, gpt_model, extra_messages)
        except Exception as e:
            print("[WARN] GPT Request Error. retry=[" + str(retry_count) +
                  "/"+str(max_retry_count)+"]"+str(e)+"\n")
            if 'Rate limit reached' in str(e):
                time.sleep(20)
            retry_count += 1
            continue

        print('------------')
        print(generated_text)
        print('------------')

        code = get_code_blocks(generated_text)

        # コード部分が空の場合
        if code == "":
            retry_count += 1
            extra_messages.append({
                "role": "assistant",
                "content": generated_text
            })
            extra_messages.append({
                "role": "user",
                "content": "Write corrected code following the output format."
            })
            continue

        # Check whether the corrected code is semantically correct
        fixed_code = regularize(code)
        if bug_code.strip() == fixed_code.strip() or (tester and not tester.is_pass(tester.tv_code(fixed_code))):
            print('the corrected code is incorrect')
            retry_count += 1
            if init_prompt == prompt:
                prompt = f'''
Please amend the provided Python program code to align with the described functionality. When suggesting code changes, adhere to these guidelines:

- Follow the output format.
- Ensure it's executable using Python's exec function.
- Retain as much of the original code's character count as possible.
- Maintain existing comments unchanged.
- Preserve whitespace and indentation.
- Maintain the original line breaks.
- Keep variable and function names intact.
- Ensure the amended code remains closer in structure to the original, rather than resembling the model solution provided.

# Problem Description
{description}

# Incorrect Code
```python
{remove_redundant_spaces(bug_code)}
```

# Model Solution (for reference)
{remove_redundant_spaces(sample_correct_code_blocks[0])}

# Output Format
"""
Amended code:
```python
...
```
"""
                '''.strip()
            else:
                extra_messages.append({
                    "role": "assistant",
                    "content": generated_text
                })
                extra_messages.append({
                    "role": "user",
                    "content": """
Your code's functionality doesn't match the model solution.
Rewrite your code to match the model solution's functionality.
If there are unnecessary identifiers in your original code, feel free to omit them for accuracy.
                    """.strip()
                })
            continue

        # Check whether the patch size is smaller than reference code
        patch_size = zss_multi_func_code_distance(bug_code, fixed_code)
        if min_patch_size <= patch_size:
            print(f'min_patch_size ({min_patch_size}) <= patch_size ({patch_size})')
            retry_count += 1
            extra_messages.append({
                "role": "assistant",
                "content": generated_text
            })
            extra_messages.append({
                "role": "user",
                "content": """
Your changes are more extensive than the model solution.
Adjust the syntax of your code to closely resemble the original, ensuring the semantics align with the model solution.
                """.strip()
            })
            continue

        try:
            if not syntax_check(code):
                raise SyntaxError('Generated code has syntax error')
            exec(code, globals())
            break
        except Exception as e:
            retry_count += 1
            # evalでエラーが発生した場合はエラー内容をプロンプトに追加してリトライ
            extra_messages.append({
                "role": "assistant",
                "content": generated_text
            })
            extra_messages.append({
                "role": "user",
                "content": f"I ran it and got an error {e}. Please correct it."
            })
            continue

    if not retry_count < max_retry_count:
        print(f"Error: Failed to fix with GPT")
        return

    return code



def _repair_code_by_gpt(prompt: str, gpt_model="gpt-3.5-turbo", extra_messages: list[str] = []) -> tuple[str, bool]:
    completion = openai.ChatCompletion.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": prompt},
            *extra_messages,
        ],
        # request_timeout=60,
        max_tokens=2024,    # 生成する文章の最大単語数
        n=1,                # いくつの返答を生成するか
        stop=None,          # 指定した単語が出現した場合、文章生成を打ち切る
        temperature=0,      # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
    )
    return completion.choices[0].message.content


def remove_redundant_spaces(code):
    code = replace_whitespace_with_tab(code)
    code = re.sub(r' *\( *', '(', code)
    code = re.sub(r' *\) *', ')', code)
    code = re.sub(r' *\{ *', '{', code)
    code = re.sub(r' *\} *', '}', code)
    code = re.sub(r' *\[ *', '[', code)
    code = re.sub(r' *\] *', ']', code)
    code = re.sub(r' *\. *', '.', code)
    code = re.sub(r' *\,', ',', code)
    code = re.sub(r' *\:', ':', code)
    code = re.sub(r'([\)\]\}])(and|or|not|in)', r'\1 \2', code)
    code = re.sub(r'(and|or|not|in|if|while|for)([\(\[\{])', r'\1 \2', code)
    code = re.sub(r'([\)\]\}])([+\-\*\/!=<>])', r'\1 \2', code)
    code = re.sub(r'([+\-\*\/=<>])([\(\[\{])', r'\1 \2', code)
    code = replace_tab_with_whitespace(code)
    return code


def replace_tab_with_whitespace(code, spaces_per_tab=4):
    lines = code.split("\n")
    for i in range(len(lines)):
        count = 0
        for char in lines[i]:
            if char == "\t":
                count += 1
            else:
                break
        lines[i] = " "*(count*spaces_per_tab) + lines[i][count:]
    return "\n".join(lines)


def replace_whitespace_with_tab(code):
    lines = code.split("\n")
    for i in range(len(lines)):
        count = 0
        for char in lines[i]:
            if char == " ":
                count += 1
            else:
                break
        lines[i] = "\t"*(count//4) + lines[i][count:]
    return "\n".join(lines)


def read_file_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except IOError:
        print(f"Error: Unable to read file '{file_path}'.")


def read_files_and_return_code_blocks(file_paths):
    code_blocks = []
    for file_path in file_paths:
        file_contents = read_file_contents(file_path)
        code_block = '```python\n{}\n```'.format(file_contents)
        code_blocks.append(code_block)
    all_code_blocks = '\n'.join(code_blocks)
    return all_code_blocks


def get_code_blocks(text: str):
    doc = Document(text)

    code_blocks = []
    for token in doc.children:
        if isinstance(token, CodeFence):
            code_blocks.append(token.children[0].content)

    return "\n\n".join(code_blocks)


def save_results(bug_code: str, description: str, sample_correct_code_blocks: list[str], gpt_model: str, patch_size: float, gpt_rep_code: Optional[str], gpt_patch_size: Optional[float]):
    data = {
        "bug_code": bug_code,
        "description": description,
        "sample_correct_code_blocks": sample_correct_code_blocks,
        "gpt_model": gpt_model,
        "patch_size": patch_size,
        "gpt_rep_code": gpt_rep_code,
        "gpt_patch_size": gpt_patch_size,
    }

    input = {key: data[key] for key in ["bug_code", "description", "sample_correct_code_blocks", "gpt_model"]}

    file_hash = _calc_hash(json.dumps(input))
    with open(f'results/json/{file_hash}.json', 'w') as file:
        file.write(json.dumps(data, indent=4))


def _calc_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


# def repair_code_by_gpt_with_retry(bug_code: str, description: str, sample_correct_code_blocks: list[str], gpt_model="gpt-3.5-turbo", max_retry_count=3, tester: Optional[Tester]=None) -> str:
#     retry_count = 0
#     extra_messages = []
#     while retry_count < max_retry_count:
#         try:
#             generated_text = repair_code_by_gpt(
#                 bug_code, description, sample_correct_code_blocks, gpt_model, extra_messages)
#         except Exception as e:
#             import sys
#             print("[WARN]ChatGPT Request Error. retry=[" + str(retry_count) +
#                   "/"+str(max_retry_count)+"]"+str(e)+"\n")
#             if 'Rate limit reached' in str(e):
#                 time.sleep(20)
#             retry_count += 1
#             continue

#         code = get_code_blocks(generated_text)

#         # コード部分が空の場合
#         if code == "":
#             retry_count += 1
#             extra_messages.append({
#                 "role": "assistant",
#                 "content": generated_text
#             })
#             extra_messages.append({
#                 "role": "user",
#                 "content": "Write a code block of code that can be executed with the Python exec function."
#             })
#             continue

#         try:
#             if not syntax_check(code):
#                 raise SyntaxError('Generated code has syntax error')
#             exec(code, globals())
#             break
#         except Exception as e:
#             retry_count += 1
#             # evalでエラーが発生した場合はエラー内容をChatGPTのパラメーターに追加してリトライ
#             extra_messages.append({
#                 "role": "assistant",
#                 "content": generated_text
#             })
#             extra_messages.append({
#                 "role": "user",
#                 "content": f"I ran it and got an error {e}. Please correct it."
#             })
#             continue

#     if not retry_count < max_retry_count:
#         print(f"Error: Failed to fix with GPT")
#         return

#     return code


# def repair_code_by_gpt(bug_code: str, description: str, sample_correct_code_blocks: list[str], gpt_model="gpt-3.5-turbo", extra_messages: list[str] = []) -> tuple[str, bool]:

#     order = f"""
#     description: "${description}"

#     ```python
#     {bug_code}
#     ```

#     Please modify the above Python program code to work correctly as specified in the description.
#     Please observe the following rules when outputting code.

#     - Code is enclosed in Markdown code blocks.
#     - Formatted to be executable with Python's exec function.
#     - Keep the modified code as many characters as possible as the original code.
#     - Do not add or delete comment text.
#     - Do not add or delete whitespace or.
#     - Do not add or delete line break characters.
#     - Do not change variable or function names.
#     - Please modify the code to be closer to the unmodified code than the following model solution.
    
#     {sample_correct_code_blocks}

#     """
#     completion = openai.ChatCompletion.create(
#         model=gpt_model,
#         messages=[
#             {"role": "system", "content": "You are an excellent Python programmer."},
#             {"role": "user", "content": order},
#             *extra_messages,
#         ],
#         max_tokens=1024,    # 生成する文章の最大単語数
#         n=1,                # いくつの返答を生成するか
#         stop=None,          # 指定した単語が出現した場合、文章生成を打ち切る
#         temperature=0.0,    # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
#     )
#     return completion.choices[0].message.content


