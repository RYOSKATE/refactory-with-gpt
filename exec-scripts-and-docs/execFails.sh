#!/bin/bash
python3 run.py -d ./data -q question_2 -s 25 -o -m -b
python3 run.py -d ./data -q question_2 -s 25 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s 50 -o -m -b -g both
python3 run.py -d ./data -q question_2 -s 100 -o -m -b -g both

rm -rf results/.gitkeep
mv results/ results-fails/
zip -r results-fails.zip results-fails

curl -F file=@./results-fails.zip  -F "initial_comment=fails終了"  -F channels=#research -F token=$SLACK_TOKEN https://slack.com/api/files.upload

sudo shutdown -h now
