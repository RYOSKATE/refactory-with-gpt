import openai
import os

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")


def Ask_ChatGPT(message):

    # 応答設定
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",     # モデルを選択
        messages=[{"role": "user", "content": message, }],
        max_tokens=1024,             # 生成する文章の最大単語数
        n=1,                # いくつの返答を生成するか
        stop=None,             # 指定した単語が出現した場合、文章生成を打ち切る
        temperature=0.5,              # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
    )

    # 応答
    response = completion.choices[0].message.content

    # 応答内容出力
    return response


# 質問内容
message = """
Please answer according to the following specifications.

# Reply format
{"code": "Source code of the modified Python program entered"}

# Instruction
You are an instructor of Python programs.
Please correct the errors in the source code submitted by your students and answer the questions by following the rules below without fail.

## Rules
- The problem statement follows the # problem statement.
- Submitted code is listed in the code block following the # submitted code.
- Correctly modify the submission code to answer the problem statement.
- Do not add or delete comment text.
- Do not add or delete whitespace or
- Do not add or delete line break characters
- Do not change variable or function names
- Modifications should be kept to a minimum.
- The reply should be in JSON format.
- The program that fixes the problem should be set in the `code` field of the output JSON

That's all for the specification.

# Problem statement
Create a program that searches an array seq from the beginning and returns the index of the first element of value less than or equal to x found.

# Submission Code
```python
def search(x, seq):
    if seq == [] or seq == ():
        return 0
    if x < seq[0]:
        return 0
    elif x > seq[len(seq)-1]:
        return len(seq)
    else:
        for i in range(len(seq)-1):
            if seq[i] == x:
                return i
            elif seq[i] <= x and seq[i+1] > x:
                return i+1
```

```
一番近い
```
"""

# ChatGPT起動
res = Ask_ChatGPT(message)

# 出力
print(res)
