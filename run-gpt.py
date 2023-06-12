import openai
import os

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")

def Ask_ChatGPT(message):
    
    # 応答設定
    completion = openai.ChatCompletion.create(
                 model    = "gpt-3.5-turbo",     # モデルを選択
                 messages = [
                    {"role":"user","content":message,}],
    
                 max_tokens  = 1024,             # 生成する文章の最大単語数
                 n           = 1,                # いくつの返答を生成するか
                 stop        = None,             # 指定した単語が出現した場合、文章生成を打ち切る
                 temperature = 0.5,              # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
    )
    
    # 応答
    response = completion.choices[0].message.content
    
    # 応答内容出力
    return response


# 質問内容
message = """
以下の仕様に従って答えてください。

# 返答のフォーマット
{"code":"入力されたPythonプログラムを修正したソースコード"}

# 命令
あなたはPythonプログラムの講師です。
生徒が提出したソースコードの誤りを、以下のルールを必ず守って修正し、回答してください。

## ルール
- 問題文は #問題文 に続いて記載されている。
- 提出コードは #提出コード に続くコードブロックに記載されている。
- 問題文の回答になるように、提出コードを正しく修正すること
- コメント文を追加・削除しないこと
- 空白文字やを追加・削除しないこと
- 改行文字を追加、削除しないこと
- 変数名や関数名を変更しないこと
- 修正は最小限にすること
- 返答はJSON形式にすること。
- 問題点を修正したプログラムは出力するJSONの`code`フィールドにセットすること

仕様は以上です。

# 問題文
配列seqを先頭から探索し、最初に見つかるx以下の値の要素のインデックスを返すプログラムを作成せよ


# 提出コード
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
"""

# ChatGPT起動
res = Ask_ChatGPT( message)

# 出力
print(res)