
# ChatGPT起動
import os
import json
from basic_framework.core_testing import Tester
from basic_framework.distance import zss_multi_func_code_distance

from basic_framework.repair_with_gpt import remove_redundant_spaces, repair_code_by_gpt_with_retry
from basic_framework.utils import regularize

def main():
    # List files in the directory "results/json"
    json_file_names = os.listdir('results/json')

    # Select top 20 files
    json_file_names = json_file_names[:100]

    # json_file_names = ['cc1ec49af3dec285599a05918d26cf0b847c657f8a2d85bf0b5cce69c1e43578.json']
    # json_file_names = ['2558a8555f9b8bf9a18a31da5b0160f87d4eccfb9d124446de558445fdeeec37.json', '6b15490da95ed587034925cf2f2a869f4774df2adb5596787f9e4a2f58b7611c.json', 'cc1ec49af3dec285599a05918d26cf0b847c657f8a2d85bf0b5cce69c1e43578.json', '4ee6cf842a7d1531bcfd39697901e7852c3e42439d8c583e2b53864add42f8ca.json']
    # json_file_names = ['553aa0f22c7d092dce412c855ae8e6eb526eaa9cdadd6162415669a45faf44d6.json']

    improved = 0
    same = 0
    worsened = 0
    tester = Tester('data/question_4')

    for json_file_name in json_file_names:
        try:
            data = read_json(f'results/json/{json_file_name}')
            print(data)
            print()

            # Whether data['bug_code'] contains 'sort_age' or not
            if 'sort_age' not in data['bug_code']:
                continue

            print(f'# Buggy Code ({json_file_name})')
            print(remove_redundant_spaces(data['bug_code']))

            for reference_code in data['sample_correct_code_blocks']:
                print('# Reference Code')
                print(remove_redundant_spaces(reference_code))

            print('# Repaired Code by GPT-3.5-Turbo with Old Prompt')
            print(remove_redundant_spaces(data['gpt_rep_code']))

            gpt_model = data['gpt_model']
            # gpt_model = 'gpt-4'
            raw_rep_code: str = repair_code_by_gpt_with_retry(data['bug_code'], data['description'], data['sample_correct_code_blocks'], gpt_model, tester=tester) or ''

            rep_code = regularize(raw_rep_code)
            patch_size = zss_multi_func_code_distance(data['bug_code'], rep_code)

            print('# Repaired Code by GPT-3.5-Turbo with New Prompt')
            print(rep_code)

            old_patch_size = data['gpt_patch_size']
            if not old_patch_size:
                old_patch_size = 999
            if not raw_rep_code or not patch_size:
                patch_size = 999

            print(f"old: {tester.is_pass(tester.tv_code(data['gpt_rep_code']))}, new: {tester.is_pass(tester.tv_code(rep_code))}\n\n")

            print(f"org: {data['patch_size']}, old: {old_patch_size}, new: {patch_size}\n\n")

            if old_patch_size > patch_size:
                improved += 1
            elif patch_size > old_patch_size:
                worsened += 1
            else:
                same += 1
        except Exception as e:
            print(f"Failed to load {json_file_name} due to {e}")

    print(f"improved: {improved}, same: {same}, worsened: {worsened}\n\n")


def read_json(file_path: str):
    with open(file_path) as f:
        data = json.load(f)
    return data


main()