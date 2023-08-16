from __future__ import annotations
from typing import Optional
import openai
import json
import hashlib
import os
from mistletoe import Document
from mistletoe.block_token import CodeFence

from basic_framework.utils import syntax_check

openai.organization = ''
openai.api_key = os.getenv("OPENAI_API_KEY")

# 実装参考:https://zenn.dev/ryo_kawamata/articles/b39ba0452fec81


def repair_code_by_gpt_with_retry(bug_code: str, description: str, sample_correct_code_blocks: list[str], gpt_model="gpt-3.5-turbo", max_retry_count=3) -> str:
    retry_count = 0
    extra_messages = []
    while retry_count < max_retry_count:
        try:
            generated_text = _repair_code_by_gpt(
                bug_code, description, sample_correct_code_blocks, gpt_model, extra_messages)
        except Exception as e:
            import sys
            print("[WARN]ChatGPT Request Error. retry=[" + str(retry_count) +
                  "/"+str(max_retry_count)+"]"+str(e)+"\n")
            retry_count += 1
            continue

        print('----------')
        print(generated_text)
        print('----------')

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
                "content": "Write a code block of code that can be executed with the Python exec function."
            })
            continue

        try:
            if not syntax_check(code):
                raise SyntaxError('Generated code has syntax error')
            exec(code, globals())
            break
        except Exception as e:
            retry_count += 1
            # evalでエラーが発生した場合はエラー内容をChatGPTのパラメーターに追加してリトライ
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



def _repair_code_by_gpt(bug_code: str, description: str, sample_correct_code_blocks: list[str], gpt_model="gpt-3.5-turbo", extra_messages: list[str] = []) -> tuple[str, bool]:

    prompt = f"""
Act as an expert in Python programming and create a patch to fix the Python program code for the problem following the rules.

# Rules
- The patch should be as close as possible to the original code.
- Keep the patch size as small as possible.
- Keep the original program structure as much as possible.
- Keep the original order of the statements as much as possible.
- Keep `pass`, `break` and `continue` statements as much as possible.
- Keep the original function and vairable names, and ignore the names in reference code.
- Keep the original parentheses as much as possible even though they are redundant.
- Keep the original statements as much as possible even though they are redundant.
- Keep the original conditional branches as much as possible even though they are redundant.

# Problem description
{description}

# Original code to be fixed
```python
{bug_code}
```
"""

    for index in range(len(sample_correct_code_blocks)):
        prompt += f"""
# Model solution {index + 1} (Ignore naming rules)
{sample_correct_code_blocks[index]}
"""

        prompt += f'''
# Output format
"""
# Fixed code with fewest changes
```python
...
```
"""
'''


    completion = openai.ChatCompletion.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": prompt},
            *extra_messages,
        ],
        max_tokens=1024,    # 生成する文章の最大単語数
        n=1,                # いくつの返答を生成するか
        stop=None,          # 指定した単語が出現した場合、文章生成を打ち切る
        temperature=0.7,    # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
    )
    return completion.choices[0].message.content


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


def save_results(bug_code: str, description: str, sample_correct_code_blocks: list[str], gpt_model: str, patch_size: float, gpt_rep_code: str, gpt_patch_size: Optional[float]):
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
        file.write(json.dumps(data))


def _calc_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
