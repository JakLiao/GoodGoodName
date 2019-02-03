from collections import defaultdict
from urllib import parse
import requests
from conf import config, constants
from data import full_wuxing_dict as fwd
from conf.config import MIN_SINGLE_NUM, MAX_SINGLE_NUM, SEX, THRESHOLD_SCORE

TESTED_FILE = 'result/name_tested.txt'  # 已经在网站测试过的名字
RESULT_FILE = 'result/name.txt'  # 结果算到的好名字
SANCAI_FILE = 'data/sancai.txt'  # 三才五行参考结语
BAIJIAXING_FILE = 'data/baijiaxing.txt'  # 百家姓最佳搭配


def getTestedDict():
    """
    获取已经测试过的列表
    """
    already_tested_dict = dict()
    with open(TESTED_FILE, 'r', encoding='utf8') as f:
        print(f.readline().strip())
        while True:
            line = f.readline().strip()
            already_tested_dict[line.split(',')[0]] = 1
            if not line:
                break
    return already_tested_dict


def getFullWordcountDict():
    """获得每个字的实际笔画数量"""
    full_word_count_dict = dict()
    for wuxing_dict in [fwd.jin_dict, fwd.mu_dict, fwd.huo_dict, fwd.shui_dict, fwd.tu_dict]:
        for num, word_list in wuxing_dict.items():
            for word in word_list:
                full_word_count_dict[word] = num
    return full_word_count_dict


FULL_WORD_COUNT_DICT = getFullWordcountDict()


def getWordWriteCountWugeCombination():
    """
    根据笔画数量，预先算出还可以的看看，一般般，还过得去
    :return: [(mid_num, last_num)]
    """
    last_name_write_num = FULL_WORD_COUNT_DICT[config.LAST_NAME]

    name_num_backup_list = []  # 根据天地人算的还可以的笔画数
    for best_ge in constants.best_num_set:
        mid_num = best_ge - last_name_write_num  # 姓名中间的字
        if mid_num < MIN_SINGLE_NUM or mid_num > MAX_SINGLE_NUM:
            continue
        for best_last_ge in constants.best_num_set:
            last_num = best_last_ge - mid_num  # 姓名最后的字
            if last_num < MIN_SINGLE_NUM or last_num > MAX_SINGLE_NUM:
                continue
            name_num_backup_list.append((mid_num, last_num))
    return name_num_backup_list


def writeDown(result, file_name):
    """
    写入文件
    :param result: 记录
    :param file_name: 文件名
    :return:
    """
    with open(file_name, 'a', encoding='utf8') as f:
        f.write(result)
        f.write('\n')
    return True


def getHtml(url, req_params=None, req_headers=None):
    if req_headers is None:
        req_headers = {}
    if req_params is None:
        req_params = {}

    try:
        common_params = dict(timeout=5, headers=req_headers)
        if req_params and req_headers:
            r = requests.get(url, params=req_params, **common_params)
        else:
            r = requests.get(url, **common_params)

        # print(r.text, )
        # print(r.url, r.encoding, r.status_code, r.headers)
        r.raise_for_status()

        return r.text
        # return response.decode('gb2312', 'ignore')
    except requests.RequestException:
        print('Oops! Timeout Error! Sorry!')


def getScore(name):
    """
    远程请求计算姓名的得分
    :param name:  姓名
    :return: 得分
    """
    try:
        surname = parse.quote(name[0:1].encode('gb2312'))
        lastname = parse.quote(name[1:].encode('gb2312'))
    except UnicodeEncodeError as e:
        print(name, '出错：', str(e))
        return
    s = parse.quote(SEX.encode('gb2312'))
    detail_url = "http://www.qimingzi.net/simpleReport.aspx?surname=" + surname + "&name=" + lastname + "&sex=" + s
    html = getHtml(detail_url)

    first_tag = '<div class="fenshu">'
    last_tag = '</div><a name="zhuanye">'
    score = html[html.index(first_tag) + len(first_tag): html.index(last_tag)]
    print("名字：{}  分数：{}".format(name, score))
    writeDown("{},{}".format(name, score), TESTED_FILE)
    if score and int(score) >= THRESHOLD_SCORE:
        # 符合阈值要求的结果记录到结果文本
        result = ','.join([name, score, detail_url])
        writeDown(result, RESULT_FILE)
    return score


def getBaijiaxingData():
    """
    百家姓以及第二字和第三字笔画数最佳搭配
    另一个版本可以参考 http://www.360doc.com/content/18/0414/14/4153217_745576219.shtml
    """
    baijiaxing_sancaiwuge_dict = defaultdict(list)
    with open(BAIJIAXING_FILE, 'r', encoding='utf8') as f:
        xing_line = []
        for linecnt, line in enumerate(f):
            line = line.strip()
            if linecnt % 3 == 0:
                xing_line = line
            elif linecnt % 3 == 1:
                combination_list = []
                combinations = line.split(',')
                for c in combinations:
                    tmp = c.split('+')
                    combination_list.append((int(tmp[0]), int(tmp[1])))
                for xing in xing_line:
                    baijiaxing_sancaiwuge_dict[xing] = combination_list
            else:
                continue  # 空行
    return baijiaxing_sancaiwuge_dict


def getSancaiData():
    """
    整理三才数理的数据

    备注：金金木重复了，被我删了
    来源百度百科：https://baike.baidu.com/item/%E4%B8%89%E6%89%8D%E6%95%B0%E7%90%86/2086868
    :return: [key: dict(    # key为天格+人格+地格
                result='',  # 吉凶结果
                evaluate='' # 评价
            ), ...]
    """
    sancai_wuxing_dict = dict()
    with open(SANCAI_FILE, 'r', encoding='utf8') as f:
        line = f.readline()
        wuxing_comb = line[:3]
        if wuxing_comb not in sancai_wuxing_dict:
            sancai_wuxing_dict[wuxing_comb] = dict(
                result='',  # 吉凶结果
                evaluate=''  # 评价
            )

        is_next_new = False
        while True:
            line = f.readline().strip()
            if is_next_new:
                wuxing_comb = line[:3]
                if wuxing_comb not in sancai_wuxing_dict:
                    sancai_wuxing_dict[wuxing_comb] = dict(
                        result='',  # 吉凶结果
                        evaluate=''  # 评价
                    )
                else:
                    print(wuxing_comb, '重复了？？')
                is_next_new = False
            else:
                if line.startswith('【'):
                    result = line[line.index('【') + 1: line.index('】')]
                    sancai_wuxing_dict[wuxing_comb]['result'] = result
                    is_next_new = True
                else:
                    sancai_wuxing_dict[wuxing_comb]['evaluate'] += line.strip()
                    is_next_new = False

            if not line:
                break
    # print('三才吉凶判断结果：', sancai_wuxing_dict)
    return sancai_wuxing_dict
