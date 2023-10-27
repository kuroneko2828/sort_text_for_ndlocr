import sys
import csv
from typing import List


def check_argv():
    if len(sys.argv) != 3:
        raise Exception(
            'Usage: python error_correction.py [source_file] [save_file]'
        )
    return


def get_error_list(error_file: str) -> List[dict]:
    with open(error_file, "r")as f:
        reader = csv.DictReader(f)
        error_list = [row for row in reader]
    return error_list


def get_text_list(text_file: str) -> List[str]:
    with open(text_file, "r")as f:
        text_list = f.read().split('\n')
    return text_list


def error_correction(text_list: List[str], error_list: List[dict]) \
        -> List[str]:
    new_text_list = []
    for text in text_list:
        new_text = text
        for error in error_list:
            new_text = new_text.replace(error['error'], error['correct'])
        new_text_list.append(new_text)
    return new_text_list


def save_file(text_list: List[str], save_file: str):
    with open(save_file, "w")as f:
        [print(text, file=f) for text in text_list]
    return


def main():
    check_argv()
    text_list = get_text_list(sys.argv[1])
    error_list = get_error_list('./error.csv')
    text_list = error_correction(text_list, error_list)
    save_file(text_list, sys.argv[2])


if __name__ == '__main__':
    main()
