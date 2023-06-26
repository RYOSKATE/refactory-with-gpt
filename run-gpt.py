
# ChatGPT起動
from basic_framework.repair_with_gpt import read_file_contents, read_files_and_return_code_blocks, repair_code_by_gpt_with_retry

bug_code_filepath = "/home/ishizue/ghq/github.com/RYOSKATE/refactory-vs-gpt/data/question_1/code/wrong/wrong_1_001.py"
description_filepath = "/home/ishizue/ghq/github.com/RYOSKATE/refactory-vs-gpt/data/question_1/description.txt"
sample_correct_code_filepaths = [
    "/home/ishizue/ghq/github.com/RYOSKATE/refactory-vs-gpt/data/question_1/code/reference/reference.py",
    "/home/ishizue/ghq/github.com/RYOSKATE/refactory-vs-gpt/data/question_1/code/correct/correct_1_001.py",
    "/home/ishizue/ghq/github.com/RYOSKATE/refactory-vs-gpt/data/question_1/code/correct/correct_1_002.py"
]

bug_code = read_file_contents(bug_code_filepath)
description = read_file_contents(description_filepath)
sample_correct_code_blocks = read_files_and_return_code_blocks(
    sample_correct_code_filepaths)

res = repair_code_by_gpt_with_retry(
    bug_code, description, sample_correct_code_blocks)

# 出力
print(res)
