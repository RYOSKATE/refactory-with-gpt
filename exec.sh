#!/bin/bash
python3 run.py -d ./data -q question_1 -s 100 -o -m -b    > results/question_1_s100_o_m_b.txt 2>> stderr.txt
python3 run.py -d ./data -q question_1 -s 100 -o -m -b -g > results/question_1_s100_o_m_b_g.txt 2>> stderr.txt
python3 run.py -d ./data -q question_2 -s 100 -o -m -b    > results/question_2_s100_o_m_b.txt 2>> stderr.txt
python3 run.py -d ./data -q question_2 -s 100 -o -m -b -g > results/question_2_s100_o_m_b_g.txt 2>> stderr.txt
python3 run.py -d ./data -q question_3 -s 100 -o -m -b    > results/question_3_s100_o_m_b.txt 2>> stderr.txt
python3 run.py -d ./data -q question_3 -s 100 -o -m -b -g > results/question_3_s100_o_m_b_g.txt 2>> stderr.txt
python3 run.py -d ./data -q question_4 -s 100 -o -m -b    > results/question_4_s100_o_m_b.txt 2>> stderr.txt
python3 run.py -d ./data -q question_4 -s 100 -o -m -b -g > results/question_4_s100_o_m_b_g.txt 2>> stderr.txt
python3 run.py -d ./data -q question_5 -s 100 -o -m -b    > results/question_5_s100_o_m_b.txt 2>> stderr.txt
python3 run.py -d ./data -q question_5 -s 100 -o -m -b -g > results/question_5_s100_o_m_b_g.txt 2>> stderr.txt
