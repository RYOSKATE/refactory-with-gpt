#!/bin/bash
python3 run.py -d ./data -q question_1 -s $1 -o -m -b -g both --gpt_model gpt-4
python3 run.py -d ./data -q question_2 -s $1 -o -m -b -g both --gpt_model gpt-4
python3 run.py -d ./data -q question_3 -s $1 -o -m -b -g both --gpt_model gpt-4
python3 run.py -d ./data -q question_4 -s $1 -o -m -b -g both --gpt_model gpt-4
python3 run.py -d ./data -q question_5 -s $1 -o -m -b -g both --gpt_model gpt-4

rm -rf results/.gitkeep
mv results/ results-gpt4-$1/
zip -r results-gpt4-$1.zip results-gpt4-$1

curl -F file=@./results-gpt4-$1.zip  -F "initial_comment=$1終了"  -F channels=#research -F token=$SLACK_TOKEN https://slack.com/api/files.upload

sudo shutdown -h now
