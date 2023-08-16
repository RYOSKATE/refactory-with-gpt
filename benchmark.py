
# ChatGPT起動
import os
import json
from basic_framework.distance import zss_multi_func_code_distance

from basic_framework.repair_with_gpt import repair_code_by_gpt_with_retry
from basic_framework.utils import regularize

def main():
    # List files in the directory "results/json"
    json_file_names = os.listdir('results/json')

    # Select top 20 files
    json_file_names = json_file_names[:30]

    # json_file_names = ['cc1ec49af3dec285599a05918d26cf0b847c657f8a2d85bf0b5cce69c1e43578.json']
    # json_file_names = ['2558a8555f9b8bf9a18a31da5b0160f87d4eccfb9d124446de558445fdeeec37.json', '6b15490da95ed587034925cf2f2a869f4774df2adb5596787f9e4a2f58b7611c.json', 'cc1ec49af3dec285599a05918d26cf0b847c657f8a2d85bf0b5cce69c1e43578.json', '4ee6cf842a7d1531bcfd39697901e7852c3e42439d8c583e2b53864add42f8ca.json']
    # json_file_names = ['78ea585010b23b20e51601e486946cd29fe37362b597bb8a2a5fa9edfb7a89f0.json', 'cc1ec49af3dec285599a05918d26cf0b847c657f8a2d85bf0b5cce69c1e43578.json']

    win = 0
    draw = 0
    lose = 0

    for json_file_name in json_file_names:
        data = read_json(f'results/json/{json_file_name}')
        print(data)
        print()

        print(f'# Buggy Code ({json_file_name})')
        print(data['bug_code'])

        for reference_code in data['sample_correct_code_blocks']:
            print('# Reference Code')
            print(reference_code)

        print('# Repaired Code by GPT-3.5-Turbo and Old Prompt')
        print(data['gpt_rep_code'])
        regularized_bug_code = regularize(data['bug_code'])
        old_patch_size = zss_multi_func_code_distance(regularized_bug_code, data['gpt_rep_code'])

        gpt_model = data['gpt_model']
        # gpt_model = 'gpt-4'
        raw_rep_code: str = repair_code_by_gpt_with_retry(data['bug_code'], data['description'], data['sample_correct_code_blocks'], gpt_model) or ''

        rep_code = regularize(raw_rep_code)
        patch_size = zss_multi_func_code_distance(regularized_bug_code, rep_code)

        print('# Repaired Code by GPT-3.5-Turbo and New Prompt')
        print(rep_code)

        if old_patch_size == 0:
            old_patch_size = 999
        if patch_size == 0:
            patch_size = 999

        if old_patch_size > patch_size:
            win += 1
        elif old_patch_size == patch_size:
            draw += 1
        else:
            lose += 1

        print(f"org: {data['patch_size']}, org (re): {zss_multi_func_code_distance(regularized_bug_code, regularize(data['sample_correct_code_blocks'][0]))}, old: {old_patch_size}, new: {patch_size}\n\n")

    print(f"win: {win}, draw: {draw}, lose: {lose}\n\n")


def read_json(file_path: str):
    with open(file_path) as f:
        data = json.load(f)
    return data


main()