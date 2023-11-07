import sys
import xml.etree.ElementTree as ET
from typing import List
import statistics

# 以下2つが改行検知に使われている関数
# 必要に応じて変更する
RATE_FOR_INDENT_USING_HEAD = 0.7  # 文頭に文字高の何倍以上の空白があれば改行とみなすか
RATE_FOR_INDENT_USING_TAIL = 1.5  # 文末に文字高の何倍以上の空白があれば改行とみなすか

# 空行検知に使われている関数
# 必要に応じて変更する
RATE_FOR_EMPTY_LINE = 2  # 文字幅の何倍以上の空白があれば空行とみなすか

PAGE_NUM_TO_GET_ROW2_Y = 5
BRACKETS_FOR_DELETE_HEAD_SPACE = ['「', '『', '【', '（']


def print_error() -> None:
    """エラーを出力して終了する
    """
    print('[Error]\nUsage: python sort_text.py [inpnut_file] [save_file] [1 or 2 (row num)]')
    exit()
    return


def arg_check() -> None:
    """コマンドライン引数が正しいかチェック
    """
    if len(sys.argv) != 4:
        print_error()
    if sys.argv[3] not in ['1', '2']:
        print_error()
    return


def get_median(lst: List[int]) -> float:
    """中央値を求める
    Parameters
    ----------
    lst : List[int]
        リスト

    Returns
    -------
    float
        中央値
    """
    half = len(lst) // 2
    new_lst = sorted(lst)
    if len(new_lst) % 2 == 0:
        mdn = (new_lst[half-1] + new_lst[half]) / 2
    else:
        mdn = new_lst[half]
    return mdn


def get_row2_y(root: ET.Element) -> float:
    """該当ページの2段目の基準を求める。
    最小のy値と最大のy値の平均を基準とする。

    Parameters
    ----------
    page : ET.Element
        ページ

    Returns
    -------
    float
        2段目の基準y値
    """
    row2_y_by_page = []
    for i, page in enumerate(root):
        if i == PAGE_NUM_TO_GET_ROW2_Y:
            break
        y_list = []
        for text in page:
            y_list.append(float(text.attrib['Y']))
        row2_y_by_page.append((max(y_list)+min(y_list))/2)
        row2_y = get_median(row2_y_by_page)
    return row2_y


def get_empty_line_width(page: ET.Element) -> float:
    """空行の基準とする幅を決定する

    Parameters
    ----------
    page : ET.Element
        ページ

    Returns
    -------
    float
        空行の基準幅
    """
    widths = []
    for text in page:
        if text.attrib['TYPE'] == '本文':
            widths.append(int(text.attrib['WIDTH']))
    return get_median(widths) * RATE_FOR_EMPTY_LINE


def exist_empty_line(ptext: dict, text: dict, empty_line_width: float):
    """空行が存在するか
    Parameters
    ----------
    ptext : dict
        過去のテキスト
    text : dict
        現在のテキスト
    empty_line_width : float
        空行幅

    Returns
    -------
    bool
        空行がそんざいするか
    """
    return (int(ptext['X']) - int(text['X']) > empty_line_width) \
        and (ptext['ROW'] == text['ROW'])


def is_indent(text: ET.Element, chara_height: float, min_y: int) -> bool:
    """インデントされているかをチェック

    Parameters
    ----------
    text : ET.Element
        xml情報付きテキスト
    chara_height : float
        インデントと判断する幅
    min_y : int
        最小のy

    Returns
    -------
    bool
        インデントされているか
    """
    return int(text['Y']) > min_y + chara_height * RATE_FOR_INDENT_USING_HEAD


def is_next_indent(text: ET.Element, chara_height: float, max_y: int) -> bool:
    """次の行がインデントされているかをチェック

    Parameters
    ----------
    text : ET.Element
        xml情報付きテキスト
    chara_height : float
        インデントと判断する幅
    max_y : int
        最大のy
    """
    return int(text['Y']) + int(text['HEIGHT']) < max_y - chara_height * RATE_FOR_INDENT_USING_TAIL


def is_utterance(text: str) -> bool:
    """テキストがセリフの最初の行か

    Parameters
    ----------
    text: str
        調査対象のテキスト

    Returns
    -------
    bool
        テキストがセリフの最初の行か
    """
    if text[0] != '「':
        return False
    if text[-1] == '」':
        return True
    else:
        if '」' not in text:
            return True
        else:
            return False


def fix_head_bracket(text_list: List[str]) -> List[str]:
    """括弧で始まる行は、最初の空白を除外する
    Parameters
    ----------
    text_list : List[str]
        テキストリスト
    """
    new_text_list = []
    for i, text in enumerate(text_list):
        if text != '' and text[0] == '　' and text[1] in BRACKETS_FOR_DELETE_HEAD_SPACE:
            new_text_list.append(text[1:])
        else:
            new_text_list.append(text)
    return new_text_list


def sort_text(page: ET.Element, row2_y: float, chara_height: float, empty_line_width: float, should_first_indent: bool)\
     -> (List[str], bool):
    """1ページ中の本文をソートする

    Parameters
    ----------
    page : ET.Element
        ページ
    row2_y : float
        2段目の基準y値
    chara_height : float
        インデントと判斷する幅
    empty_line_width : float
        空行幅
    is_first_indent : bool
        最初の文が字下げされるか

    Returns
    -------
    List[str]
        ソートしたテキストリスト
    bool
        最初の文が字下げされているか
    bool
        次のページの最初の文が字下げされるか
    """
    text_list = []
    for text in page:
        if text.attrib['TYPE'] != '本文':
            continue
        if 'STRING' not in text.attrib.keys() or text.attrib['STRING'] == '':
            continue
        text_list.append(text.attrib)
        if int(text_list[-1]['Y']) > row2_y:
            text_list[-1]['ROW'] = 2
        else:
            text_list[-1]['ROW'] = 1
    if text_list == []:
        return [], False, False

    text_list = sorted(text_list, key=lambda x: int(x['X']), reverse=True)
    text_list = sorted(text_list, key=lambda x: int(x['ROW']))
    row1_min_y = min([int(text['Y']) for text in text_list])
    row2_min_y = min([int(text['Y']) for text in text_list if text['ROW'] == 2]+[float('inf')])
    row1_max_y = max([int(text['Y']) + int(text['HEIGHT']) for text in text_list if text['ROW'] == 1])
    row2_max_y = max([int(text['Y']) + int(text['HEIGHT']) for text in text_list if text['ROW'] == 2]+[float('-inf')])
    sorted_text = []
    if (is_indent(text_list[0], chara_height, row1_min_y) or should_first_indent)\
            and (not is_utterance(text_list[0]['STRING'])):
        tmp_text = '　'
    else:
        tmp_text = ''
    ptext = text_list[0]
    next_indent = False
    for text in text_list:
        min_y = [row1_min_y, row2_min_y][text['ROW']-1]
        max_y = [row1_max_y, row2_max_y][text['ROW']-1]
        if tmp_text not in ['', '　']:
            if exist_empty_line(ptext, text, empty_line_width):
                sorted_text.append(tmp_text)
                sorted_text.append('')
                if is_utterance(text['STRING']):
                    tmp_text = ''
                else:
                    tmp_text = '　'
            elif is_utterance(text['STRING']):
                sorted_text.append(tmp_text)
                tmp_text = ''
            elif is_indent(text, chara_height, min_y) or next_indent:
                sorted_text.append(tmp_text)
                tmp_text = '　'
        tmp_text += text['STRING']
        ptext = text
        next_indent = is_next_indent(text, chara_height, max_y)
    if tmp_text not in ['', '　']:
        sorted_text.append(tmp_text)
    sorted_text = fix_head_bracket(sorted_text)
    is_first_indent = is_indent(text_list[0], chara_height, row1_min_y) or is_utterance(text_list[0]['STRING']) or should_first_indent
    is_next_page_indent = is_next_indent(text_list[-1], chara_height, row1_max_y) or is_utterance(text_list[0]['STRING'])
    return sorted_text, is_first_indent, is_next_page_indent


def get_chara_height(page: ET.Element) -> float:
    """字下げと判断するサイズを取得する

    Parameters
    ----------
    page : ET.Element
        ページ

    Returns
    -------
    float
        字下げと判断するサイズ
    """
    chara_sizes = []
    for text in page:
        if text.attrib['TYPE'] != '本文':
            continue
        if 'STRING' not in text.attrib.keys() or text.attrib['STRING'] == '':
            continue
        chara_size = int(text.attrib['HEIGHT'])/len(text.attrib['STRING'])
        chara_sizes.append(chara_size)
    #chara_size = statistics.median(chara_sizes)
    if len(chara_sizes) == 0:
        return False
    else:
        chara_size = sum(chara_sizes)/len(chara_sizes)
    return chara_size


def get_text(input_file: str, row_num: int) -> List[str]:
    """xmlファイルからテキストデータを取得する

    Parameters
    ----------
    input_file : str
        OCRの出力ファイル (XML)
    row_num : int
        何段組か

    Returns
    -------
    List[str]
        取得したテキスト
    """
    text = []
    input_file = sys.argv[1]
    with open(input_file, 'r')as f:
        tree = ET.parse(f)
    root = tree.getroot()

    if row_num == 1:
        row2_y = float('inf')
    else:
        row2_y = get_row2_y(root)

    is_next_page_indent = True

    for i, page in enumerate(root):
        chara_height = get_chara_height(page)
        if chara_height is False:
            continue
        empty_line_width = get_empty_line_width(page)
        new_text, is_first_indent, is_next_page_indent = sort_text(page, row2_y, chara_height, empty_line_width, is_next_page_indent)
        if is_first_indent:
            text.extend(new_text)
        else:
            if new_text != []:
                if text == []:
                    text.append(new_text[0])
                else:
                    text[-1] += new_text[0]
                if len(new_text) > 1:
                    text.extend(new_text[1:])
    return text


def save_text(text: List[str], save_file: str) -> None:
    """テキストを保存する

    Parameters
    ----------
    text : List[str]
        テキスト
    save_file : str
        テキストを保存するファイル
    """
    with open(save_file, "w")as f:
        [print(t, file=f) for t in text]
    return


def main():
    arg_check()
    text = get_text(sys.argv[1], int(sys.argv[3]))
    save_text(text, sys.argv[2])


if __name__ == '__main__':
    main()
