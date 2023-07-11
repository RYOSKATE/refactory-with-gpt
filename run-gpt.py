
# ChatGPT起動
import os
from basic_framework.repair_with_gpt import read_file_contents, read_files_and_return_code_blocks, repair_code_by_gpt_with_retry

path = os.getcwd()
bug_code_filepath = path + "/data/question_1/code/wrong/wrong_1_001.py"
description_filepath = path + "/data/question_1/description.txt"
sample_correct_code_filepaths = [
    path + "/data/question_1/code/reference/reference.py",
    path + "/data/question_1/code/correct/correct_1_001.py",
    path + "/data/question_1/code/correct/correct_1_002.py"
]

bug_code = read_file_contents(bug_code_filepath)
description = read_file_contents(description_filepath)
sample_correct_code_blocks = read_files_and_return_code_blocks(
    sample_correct_code_filepaths)

gpt_model="gpt-3.5-turbo"
res = repair_code_by_gpt_with_retry(
    bug_code, description, sample_correct_code_blocks, gpt_model)

# 出力
print(res)
