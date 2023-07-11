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


curl --location 'https://slack.com/api/chat.postMessage' \
--header 'Content-type: application/json' \
--header "Authorization: Bearer $SLACK_TOKEN" \
--data '{
  "channel": "#research",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "'$1が終了しました'"
      }
    }
  ]
}'

sudo shutdown -h now