#!/bin/bash
python3 run.py -d ./data -q question_1 -s $1 -o -m -b   
python3 run.py -d ./data -q question_1 -s $1 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s $1 -o -m -b   
python3 run.py -d ./data -q question_2 -s $1 -o -m -b -g both
python3 run.py -d ./data -q question_3 -s $1 -o -m -b   
python3 run.py -d ./data -q question_3 -s $1 -o -m -b -g both
python3 run.py -d ./data -q question_4 -s $1 -o -m -b   
python3 run.py -d ./data -q question_4 -s $1 -o -m -b -g both
python3 run.py -d ./data -q question_5 -s $1 -o -m -b   
python3 run.py -d ./data -q question_5 -s $1 -o -m -b -g both

rm -rf results/20230703
zip -r results-$1.zip results

curl -F file=@./results-$1.zip  -F "initial_comment=$1終了"  -F channels=#research -F token=$SLACK_TOKEN https://slack.com/api/files.upload
