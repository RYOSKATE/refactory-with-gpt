# with GPT 用

## セットアップ

```bash
# for 5.10.0-23-cloud-amd64 #1 SMP Debian 5.10.179-1 (2023-05-12) x86_64 GNU/Linux
:> agents_to_install.csv && \
echo '"projects/research-392412/zones/asia-northeast1-b/instances/ishizue-refactory-with-gpt","[{""type"":""ops-agent""}]"' >> agents_to_install.csv && \
curl -sSO https://dl.google.com/cloudagents/mass-provision-google-cloud-ops-agents.py && \
python3 mass-provision-google-cloud-ops-agents.py --file agents_to_install.csv

sudo apt update -y
sudo apt install -y git curl unzip zip
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.12.0
echo ". \$HOME/.asdf/asdf.sh" >> ~/.bashrc
echo ". \$HOME/.asdf/completions/asdf.bash" >> ~/.bashrc
source  ~/.bashrc
asdf plugin-add python
git clone このリポジトリ
cd refactory-vs-gpt
```

```bash
asdf install
#python3 -m pip install pip==23.1.2
pip3 install -r requirements.txt
unzip data.zip
```

## 実行方法

```bash
export OPENAI_API_KEY='sk-...'
#Q1～Q5でQ3が一番早く終わる
python3 run.py -d ./data -q question_3 -s 100 -o -m -b
# -g bothをつけるとgptを利用した修正を行う、 -g onlyのときはgptだけで修正する
python3 run.py -d ./data -q question_3 -s 100 -o -m -b -g both
```

results/に\*.txt で途中経過や最後にサマリを出力。
最後まで実行すると csv 形式で出力。

```bash
# 放置実行用
export SLACK_TOKEN="xoxb-..."
export OPENAI_API_KEY='sk-...'
nohup ./exec.sh 100 &
```

# メモ

GPT 修正の関数のみ個別に動作確認のために呼び出す場合

```bash
export OPENAI_API_KEY='sk-...'
python3 run-gpt.py
```

## 論文メモ

### 用語

|ID|Description|Avg. #Lines #Correct #Incorrect %CFG Match Repair Rate Avg. Time Relative Patch
of Code Attempt Attempt W/O R W/ R Taken (sec) Size (RPS)

![Alt text](image.png)

- “% CFG Match”：制御フロー構造が一致する正しい回答が見つかった割合。
  (W/O R はリファクタリングなし、W/ R はリファクタリングあり)
  Repair rate, average time-taken and relative patch size per assignment are shown for Refactory (and for Clara in brackets).
- CFG: control flow graphs
- mut: # 1.2 structure mutation
- TED：Tree-Edit-Distance。木の距離。
- Patch Size：バグコードと、修正コードの TED(AST の距離)
- REP: Relative Patch Size: Patch Size を元のバグコードのサイズで正規化した値(Clara で定義)

## Refactory 実装内容メモ

- パラメータで指定した Question X を対象に実行
- Question X の"生徒の誤回答提出コード","生徒の正解提出コード", "模範解答コード"のコードを読み込む。
- サンプリングレートリストの値ぶんだけループする
  - "模範解答コード"を"正しい回答リスト"に追加する
  - "サンプリングレート"が 1 ～ 100 ならその割合だけ"生徒の正解提出コード"も追加する。
  - "正しい回答リスト"のコードそれぞれの"構文データ"を作成しておく。
  - "生徒の誤回答提出コード"リストの数だけループする
    - "正しい回答リスト"の中に、"誤回答"と、定義されている関数&その中の変数や構造が一致するコードがあるかチェックし、あれば match_ori=1, なければ 0
    - total_time の時計スタート
    - バグコードのシンタックスチェック
      - シンタックスエラーがあれば`fail_syntax_error`で次のループへ。
      - ※論文：以下の(誤回答)提出コードは除外する。
        - 構文エラーが含まれていたり、
        - 基本ブロックが 1 つしかなかったり (trivial assignments)、
        - または Refactory や Clara の実装でサポートされていない Python 言語の機能(ラムダ関数、例外処理、オブジェクト指向プログラミングの概念など)を利用しているものを除外します。
    - 誤回答コードの"構文データ"を作成する。
    - A\*(A-star アルゴリズム)で online refactoring の時計スタート(rc:refactoring code)
    - 実施。修正コードのマップを作る。
      - online refactoring の時計ストップ
      - gcr の時計スタート
      - 修正コードのマップの中で一番誤回答コードと距離(TED)が小さい修正コードを見つける。
      - gcr の時計ストップ
    - 一番 TED が小さい修正コードを、"暫定正解コード"として記録
    - バグ修正処理開始
      - 時計スタート
      - "誤回答"コードと"暫定正解コード"の構文データが同じなら match=1, mut=0
      - 違っていれば# 1.2 structure mutation を実施.時計記録。"誤回答"コードは mutate したものに上書き。mutate フラグオフなら"fail_no_match"で処理終了。
      - align_bug_code に"誤回答"コードを記録(元から一致 or mutate すれば一致するはず)
      - ブロックや変数の変更を行いテストしながら一番近いコードを探し、final_rep_code に記録。
      - final_rep_code をテストして全部のテストに通っていれば、mutate の有無で success_w_mut または success_wo_mut を記録
      - テストに通らず、タイムアウトなら fail_timeout、それ以外なら fail_other、何か例外なら fail_exception
      - total_time の時計ストップ。
        - タイムアウト時間を超えていたら"fail_timeout"
      - success なら、
        - パッチサイズ(元の誤回答コードと、修正コード)
        - RPS(元の誤回答コードと、修正コード)を記録

## 方針

- refactory が見つけた最も良い修正コード(パッチサイズが小さいもの上位 3 つくらい)をインプットにして GPT にこれより良い(小さい)の見つけて、と投げて良いのが見つかったらそれを採用する方針
  - これで完全上位互換になるはず(time 以外は)。
- 模範解答セットが少ないときはたぶん勝つ
  - それこそ模範解答 0 個でも GPT ならコード直してくれる

## やったこと

- Refactory の中身把握
  - `## Refactory 実装内容メモ`
  - ここが処理の中心`basic_framework/repair.py`
- gpt 処理追加
  - `basic_framework/repair_with_gpt.py`
    - 処理本体はここ。
  - `run-gpt.py`
    - 試しに動かすようのやつはここ.`python run run-gpt.py`
  - `basic_framework/repair.py`
    - `basic_framework/repair.py`に`repair_with_gpt`する処理や計測項目追加
- 比較実行
  - `## 実行結果メモ`に。
