""" from https://github.com/keithito/tacotron """

import itertools
import inflect
import re


_inflect = inflect.engine()
_comma_number_re = re.compile(r"([0-9][0-9\,]+[0-9])")
_decimal_number_re = re.compile(r"([0-9]+\.[0-9]+)")
_pounds_re = re.compile(r"£([0-9\,]*[0-9]+)")
_dollars_re = re.compile(r"\$([0-9\.\,]*[0-9]+)")
_ordinal_re = re.compile(r"[0-9]+(st|nd|rd|th)")
_number_re = re.compile(r"[0-9]+")


def _remove_commas(m):
    return m.group(1).replace(",", "")


def _expand_decimal_point(m):
    return m.group(1).replace(".", " point ")


def _expand_dollars(m):
    match = m.group(1)
    parts = match.split(".")
    if len(parts) > 2:
        return match + " dollars"  # Unexpected format
    dollars = int(parts[0]) if parts[0] else 0
    cents = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if dollars and cents:
        dollar_unit = "dollar" if dollars == 1 else "dollars"
        cent_unit = "cent" if cents == 1 else "cents"
        return "%s %s, %s %s" % (dollars, dollar_unit, cents, cent_unit)
    elif dollars:
        dollar_unit = "dollar" if dollars == 1 else "dollars"
        return "%s %s" % (dollars, dollar_unit)
    elif cents:
        cent_unit = "cent" if cents == 1 else "cents"
        return "%s %s" % (cents, cent_unit)
    else:
        return "zero dollars"


def _expand_ordinal(m):
    return _inflect.number_to_words(m.group(0))


def _expand_number(m):
    num = int(m.group(0))
    if num > 1000 and num < 3000:
        if num == 2000:
            return "two thousand"
        elif num > 2000 and num < 2010:
            return "two thousand " + _inflect.number_to_words(num % 100)
        elif num % 100 == 0:
            return _inflect.number_to_words(num // 100) + " hundred"
        else:
            return _inflect.number_to_words(
                num, andword="", zero="oh", group=2
            ).replace(", ", " ")
    else:
        return _inflect.number_to_words(num, andword="")


def normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_pounds_re, r"\1 pounds", text)
    text = re.sub(_dollars_re, _expand_dollars, text)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = re.sub(_ordinal_re, _expand_ordinal, text)
    text = re.sub(_number_re, _expand_number, text)
    return text

def _expand_chinese_decimal_point(m):
    return m.group(1).replace('.', '点')

def _expand_chinese_number(m, big=False, simp=True, o=False, twoalt=False):
    num = int(m.group(0))
    """
    Converts numbers to Chinese representations.
    `big`   : use financial characters.
    `simp`  : use simplified characters instead of traditional characters.
    `o`     : use 〇 for zero.
    `twoalt`: use 两/兩 for two when appropriate.
    Note that `o` and `twoalt` is ignored when `big` is used,
    and `twoalt` is ignored when `o` is used for formal representations.
    """
    # check num first
    nd = str(num)
    if abs(float(nd)) >= 1e48:
        raise ValueError('number out of range')
    elif 'e' in nd:
        raise ValueError('scientific notation is not supported')
    c_symbol = '正负点' if simp else '正負點'
    if o:  # formal
        twoalt = False
    if big:
        c_basic = '零壹贰叁肆伍陆柒捌玖' if simp else '零壹貳參肆伍陸柒捌玖'
        c_unit1 = '拾佰仟'
        c_twoalt = '贰' if simp else '貳'
    else:
        c_basic = '〇一二三四五六七八九' if o else '零一二三四五六七八九'
        c_unit1 = '十百千'
        if twoalt:
            c_twoalt = '两' if simp else '兩'
        else:
            c_twoalt = '二'
    c_unit2 = '万亿兆京垓秭穰沟涧正载' if simp else '萬億兆京垓秭穰溝澗正載'
    revuniq = lambda l: ''.join(k for k, g in itertools.groupby(reversed(l)))
    nd = str(num)
    result = []
    if nd[0] == '+':
        result.append(c_symbol[0])
    elif nd[0] == '-':
        result.append(c_symbol[1])
    if '.' in nd:
        integer, remainder = nd.lstrip('+-').split('.')
    else:
        integer, remainder = nd.lstrip('+-'), None
    if int(integer):
        result.append(''.join(c_basic[int(ch)] for ch in integer))
        # splitted = [integer[max(i - 4, 0):i]
        #             for i in range(len(integer), 0, -4)]
        # intresult = []
        # for nu, unit in enumerate(splitted):
        #     # special cases
        #     if int(unit) == 0:  # 0000
        #         intresult.append(c_basic[0])
        #         continue
        #     elif nu > 0 and int(unit) == 2:  # 0002
        #         intresult.append(c_twoalt + c_unit2[nu - 1])
        #         continue
        #     ulist = []
        #     unit = unit.zfill(4)
        #     for nc, ch in enumerate(reversed(unit)):
        #         if ch == '0':
        #             if ulist:  # ???0
        #                 ulist.append(c_basic[0])
        #         elif nc == 0:
        #             ulist.append(c_basic[int(ch)])
        #         elif nc == 1 and ch == '1' and unit[1] == '0':
        #             # special case for tens
        #             # edit the 'elif' if you don't like
        #             # 十四, 三千零十四, 三千三百一十四
        #             ulist.append(c_unit1[0])
        #         elif nc > 1 and ch == '2':
        #             ulist.append(c_twoalt + c_unit1[nc - 1])
        #         else:
        #             ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
        #     ustr = revuniq(ulist)
        #     if nu == 0:
        #         intresult.append(ustr)
        #     else:
        #         intresult.append(ustr + c_unit2[nu - 1])
        # result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    if remainder:
        result.append(c_symbol[2])
        result.append(''.join(c_basic[int(ch)] for ch in remainder))
    return ''.join(result)


def normalize_chinese_numbers(text):
    text = re.sub(_decimal_number_re, _expand_chinese_decimal_point, text)
    text = re.sub(_number_re, _expand_chinese_number, text)
    return text