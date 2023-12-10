#!/bin/bash
python3 run.py -d ./data -q question_2 -s 0 -o -m -b
python3 run.py -d ./data -q question_2 -s 0 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s 20 -o -m -b
python3 run.py -d ./data -q question_2 -s 20 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s 40 -o -m -b
python3 run.py -d ./data -q question_2 -s 40 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s 60 -o -m -b
python3 run.py -d ./data -q question_2 -s 60 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s 80 -o -m -b
python3 run.py -d ./data -q question_2 -s 80 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s 100 -o -m -b
python3 run.py -d ./data -q question_2 -s 100 -o -m -b -g both

# rm -rf results/.gitkeep
# mv results/ results-$1/
# zip -r results-$1.zip results-$1

# curl -F file=@./results-$1.zip  -F "initial_comment=$1終了"  -F channels=#research -F token=$SLACK_TOKEN https://slack.com/api/files.upload

# sudo shutdown -h now
