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