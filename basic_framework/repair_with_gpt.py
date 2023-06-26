from __future__ import annotations
import openai
import os
from mistletoe import Document
from mistletoe.block_token import CodeFence

from basic_framework.utils import syntax_check

openai.organization = ''
openai.api_key = os.getenv("OPENAI_API_KEY")


def repair_code_by_gpt_with_retry(bug_code: str, description: str, sample_correct_code_blocks: list[str], max_retry_count=3) -> str:
    retry_count = 0
    extra_messages = []
    while retry_count < max_retry_count:
        try:
            generated_text = repair_code_by_gpt(
                bug_code, description, sample_correct_code_blocks)
        except Exception as e:
            import sys
            print(str(e)+"\n", file=sys.stderr)
            retry_count += 1
            continue

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


def repair_code_by_gpt(bug_code: str, description: str, sample_correct_code_blocks: list[str]) -> tuple[str, bool]:

    order = f"""
    description: "${description}"

    ```python
    {bug_code}
    ```

    Please modify the above Python program code to work correctly as specified in the description.
    Please observe the following rules when outputting code.

    - Code is enclosed in Markdown code blocks.
    - Formatted to be executable with Python's exec function.
    - Keep the modified code as many characters as possible as the original code.
    - Do not add or delete comment text.
    - Do not add or delete whitespace or.
    - Do not add or delete line break characters.
    - Do not change variable or function names.
    - Please modify the code to be closer to the unmodified code than the following model solution.
    
    {sample_correct_code_blocks}

    """
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an excellent Python programmer."},
            {"role": "user", "content": order},
        ],
        max_tokens=1024,             # 生成する文章の最大単語数
        n=1,                # いくつの返答を生成するか
        stop=None,             # 指定した単語が出現した場合、文章生成を打ち切る
        temperature=0.5,              # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
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
