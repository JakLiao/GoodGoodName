#!/usr/bin/python
# -*-coding:utf-8-*-
import random
import traceback

import constants

__author__ = 'HaoHao de Father'

from requests import RequestException
import time
import urllib
import requests
from http import cookiejar
from urllib import request
from urllib import parse
import self_wuxing_dict as w  # 自选用 self_wuxing_dict ，全集用 wuxing_dict

g_selected_write_dict = {
    '水': w.shui_dict,
    '火': w.huo_dict,
    '木': w.mu_dict,
    '金': w.jin_dict,
    '土': w.tu_dict
}
names_url = "http://www.qimingzi.net/showNames.aspx"
base_url = "http://www.qimingzi.net/"

FIRST_NAME = '廖'  # 姓氏
FIRST_NAME_WRITE_NUM = 14  # 康熙字典乾隆字典的笔画，其他不算

MIN_SINGLE_NUM = 2  # 单个字最少笔画过滤
MAX_SINGLE_NUM = 20  # 单个字最多笔画过滤
RESULT_UNKNOWN = '结果未知'
SELECTED_SANCAI = ['大吉', '中吉']  # 如果为None就不特意选最好的

SEX = '女'  # 男 或者 女
RESULT_FILE = 'name.txt'  # 结果算到的好名字
TESTED_FILE = 'name_tested.txt'  # 已经在网站测试过的名字
SANCAI_FILE = 'sancai.txt'  # 三才五行参考结语
THRESHOLD_SCORE = 85  # 三才五格测试最低能接受的得分

'''
这个喜用神自己在网站查查
'''
SELECTED_XITONGSHEN = '木'  # 已知的喜用神

global_sancai_wuxing_dict = {}

params = {'surname': FIRST_NAME, 'sex': SEX}

# 首先在http://www.qimingzi.net/ 网站提交基本信息，开始起名，把cookie复制下来
headers = {"Cookie": "bdshare_firstime=1535117517052; __tins__5033285=%7B%22sid%22%3A%201535177057246%2C%20%22vd%22"
                     "%3A%201%2C%20%22expires%22%3A%201535178857246%7D; __51cke__=; __51laig__=8; "
                     "Hm_lvt_4baf75bdd37d2c14c33b580be5423f7f=1535117517; "
                     "Hm_lpvt_4baf75bdd37d2c14c33b580be5423f7f=1535177058; userSurname=%e5%bb%96; userSex=2; "
                     "searchType=report; otherPara=%e5%b9%bf%e4%b8%9c%e7%9c%81%e6%b7%b1%e5%9c%b3%7c10%7c%e6%9c%a8%7c"
                     "%3cb%3e%e4%ba%94%e8%a1%8c%e5%88%86%e6%9e%90%3c%2fb%3e%ef%bc%9a%e5%85%ab%e5%ad%97%e8%bf%87%e7%a1"
                     "%ac%ef%bc%8c%e5%85%ab%e5%ad%97%e5%96%9c%e6%9c%a8%ef%bc%8c%e8%b5%b7%e5%90%8d%e6%9c%80%e5%a5%bd"
                     "%e7%94%a8%e4%ba%94%e8%a1%8c%e5%b1%9e%e6%80%a7%e4%b8%ba%e3%80%8c%3cfont+color%3d0033FF%3e%3cb%3e"
                     "%e6%9c%a8%3c%2fb%3e%3c%2ffont%3e%e3%80%8d%e7%9a%84%e5%ad%97%3cbr%3e; year=2018; month=8; "
                     "date=19; hour=18; minute=25",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0"}


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
    except RequestException:
        print('Oops! Timeout Error! Sorry!')


def getCookie(url):
    cj = cookiejar.LWPCookieJar()
    handler = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)
    r = urllib.request.Request(url)
    result = opener.open(r)
    print(result.read())

    ret = ''
    if cj:
        for ck in cj:
            print(ck.name, ck.value)
            ret = (ck.name + "=" + ck.value) + ";" + ret
        return ret
    else:
        return 'no cookie founded'


def getScore(name):
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
        result = ','.join([name, score, detail_url])
        writeDown(result, RESULT_FILE)


def getNameList():
    html = getHtml(names_url, params, headers)
    first_tag = html.index('<div class="scon" >')
    last_tag = html.index('<div style="padding-left:150px;">')
    target_content = html[first_tag: last_tag]
    print(target_content)


def writeDown(result, file_name):
    with open(file_name, 'a', encoding='utf8') as f:
        f.write(result)
        f.write('\n')


def getTestedDict():
    already_tested_dict = dict()
    with open(TESTED_FILE, 'r', encoding='utf8') as f:
        print(f.readline().strip())
        while True:
            line = f.readline().strip()
            already_tested_dict[line.split(',')[0]] = 1
            if not line:
                break
    return already_tested_dict


def getMyWifeSelection():
    """
    方法一：
    老婆根据五行缺火木，选出的喜欢的字，组合成名字
    :return: 名字列表
    """
    name_list = []
    five_hang_mu = ['若', '蕴', '栩', '茗', '吟', '蔚', '柠']
    five_hang_huo = ['憬', '炯', '尔', '恬', '粼', '燃']
    # 组合火和木的喜欢的名字 结果：廖若尔,90  廖若粼,90
    for mid in five_hang_mu:
        for last in five_hang_huo:
            name_list.append(FIRST_NAME + mid + last)
    for mid in five_hang_huo:
        for last in five_hang_mu:
            name_list.append(FIRST_NAME + mid + last)
    print('老婆选的待测试名字列表： ', name_list)
    return name_list


def calHaohaoWuge(verbose=True):
    """
    方法二：
    三才五格 最适合的计算
    配置在constants.py中，根据个人情况配置
    只考虑名字三个字的情况

    三才五格计算公式参考： http://www.360doc.com/content/18/0521/14/1654071_755714474.shtml
    根据笔画查字 ref：http://www.zdic.net/z/kxzd/zbh/
    :return:
    """
    tian_ge = FIRST_NAME_WRITE_NUM + 1
    write_num_set = set()
    name_num_backup_list = []  # 根据天地人算的还可以的笔画数
    # 先算出还可以的看看，一般般，还过得去
    for best_ge in constants.best_num_set:
        mid_num = best_ge - FIRST_NAME_WRITE_NUM
        if mid_num < MIN_SINGLE_NUM or mid_num > MAX_SINGLE_NUM:
            continue
        for best_last_ge in constants.best_num_set:
            last_num = best_last_ge - mid_num
            if last_num < MIN_SINGLE_NUM or last_num > MAX_SINGLE_NUM:
                continue
            name_num_backup_list.append((mid_num, last_num))

    # 结果总格和外格计算
    best_wuge_combination = []
    for (mid_num, last_num) in name_num_backup_list:
        zong_ge = FIRST_NAME_WRITE_NUM + mid_num + last_num
        ren_ge = FIRST_NAME_WRITE_NUM + mid_num
        di_ge = mid_num + last_num
        wai_ge = zong_ge - ren_ge + 1
        if zong_ge not in constants.best_num_set or wai_ge not in constants.best_num_set:
            continue
        # 计算三才
        sancai, sancai_result, sancai_evaluate = calHoahaoSancai(tian_ge, ren_ge, di_ge)
        if '凶' in sancai_result or sancai_result == RESULT_UNKNOWN:
            print('过滤判断为凶或未知的三才：', sancai, sancai_result)
            continue
        if SELECTED_SANCAI and sancai_result not in SELECTED_SANCAI:  # 必须要非常旺的才要
            continue
        # 计入结果
        best_wuge_combination.append((mid_num, last_num, sancai, sancai_result))
        write_num_set.add(mid_num)
        write_num_set.add(last_num)

    if verbose:
        output_num_list = list(write_num_set)
        output_num_list.sort()
        print('**好好五格名字笔画数量：', len(best_wuge_combination), best_wuge_combination)
        for o in best_wuge_combination:
            print('\t', o)
        print('\t笔画包括：', output_num_list, '(根据笔画去查康熙字典)')

    return best_wuge_combination


def getSancaiWuxing(x_ge):
    """
    根据天格、人格、地格计算得出五行属性
    尾数为1，2五行为木；尾数为3，4五行为火；尾数为5，6五行为土；尾数为7，8五行为金；尾数为9，0五行为水
    :param x_ge: x格
    :return: 五行
    """
    wuxing = ''
    if (x_ge % 10) in [1, 2]:
        wuxing = '木'
    elif (x_ge % 10) in [3, 4]:
        wuxing = '火'
    elif (x_ge % 10) in [5, 6]:
        wuxing = '土'
    elif (x_ge % 10) in [7, 8]:
        wuxing = '金'
    elif (x_ge % 10) in [9, 0]:
        wuxing = '水'
    return wuxing


def calHoahaoSancai(tian_ge, ren_ge, di_ge):
    """
    三才五行吉凶计算
    :return:
    :param tian_ge:  天格
    :param ren_ge:  人格
    :param di_ge:  地格
    :return:
    """
    sancai = getSancaiWuxing(tian_ge) + getSancaiWuxing(ren_ge) + getSancaiWuxing(di_ge)
    if sancai in global_sancai_wuxing_dict:
        data = global_sancai_wuxing_dict[sancai]
        return sancai, data['result'], data['evaluate']
    else:
        return sancai, RESULT_UNKNOWN, None


def calHaohaoXiyongshen():
    """
    方法三：
    五行（喜用神）最适合的计算
    计算你名字的五行与笔划的时候，按照乾隆字典计算
    12345对应水火木金土，67890也对应水火木金土，12345为阳，67890为阴，
    故甲阳木3，乙阴木8，丙阳火2，丁阴火7，庚阳金4，辛阴金9，壬阳水1，癸阴水6，戊阳土5，己阴土0
    参考：https://www.lnka.cn/article/topic2285.html
    :return:
    """
    best_xiyongshen_combination = []
    best_num_combination = calHaohaoWuge(False)

    # 不同流派可能求余算法不同，这里用易经的，不一致的情况可以自己改改
    mu_val = [3, 8]
    huo_val = [2, 7]
    jin_val = [4, 9]
    shui_val = [1, 6]
    tu_val = [5, 0]
    selected_dict = {'水': shui_val, '火': huo_val, '木': mu_val, '金': jin_val, '土': tu_val}
    for (mid_num, last_num, _, _) in best_num_combination:
        if (mid_num % 10 in selected_dict[SELECTED_XITONGSHEN]) \
                and (last_num % 10 in selected_dict[SELECTED_XITONGSHEN]):
            best_xiyongshen_combination.append((mid_num, last_num))
    print('**好好喜用神五行名字笔画数量：', len(best_xiyongshen_combination), best_xiyongshen_combination)
    return best_xiyongshen_combination


def calHaohaoPianpang():
    """
    方法四：
    五行（偏旁） 最适合的计算
    首先要知道喜用神
    :return:
    """
    pass  # 这一步需要人工从wuxing_dict.py筛选


def calSelection(name_list):
    """
    从选出的名字列表中，请求起名网站查看分数
    :param name_list:
    :return:
    """
    already_tested_dict = getTestedDict()
    for name in name_list:
        if name in already_tested_dict:
            continue
        getScore(name)
        # 按照正常用户的速度来访问，避免请求太快被封掉了
        time.sleep(random.randint(4, 6))


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
    print('三才吉凶判断结果：', sancai_wuxing_dict)
    return sancai_wuxing_dict


def getSancaiWugeSelection(best_combination):
    """
    通过三才五格算出的笔画数，找出匹配的名字清单
    :param best_combination:
    :return:
    """
    write_num_dict = g_selected_write_dict[SELECTED_XITONGSHEN]
    name_set = set()
    for x in best_combination:
        mid_write_num = x[0]
        last_write_num = x[1]
        if mid_write_num not in write_num_dict or last_write_num not in write_num_dict:
            continue
        mid_selection = write_num_dict[mid_write_num]
        last_selection = write_num_dict[last_write_num]

        # 仅仅测试下笔画配比
        # name_set.add(FIRST_NAME + mid_selection[0] + last_selection[0])

        # 所有名字都测试下
        for m in mid_selection:
            for l in last_selection:
                name_set.add(FIRST_NAME + m + l)  # 反过来的话人格和地格就不对了
    print('三才五格待测试名字列表：', len(name_set), name_set)
    return name_set


def calDictWuge():
    """
    方法七：
    通过字典枚举暴力遍历所有组合

    运算后结果看name.txt, 笔画列表放入 calDictWugeAfter()， 方便后续快速运算
    :return:
    """
    combination = []
    write_num_dict = g_selected_write_dict[SELECTED_XITONGSHEN]
    for write_num1, _ in write_num_dict.items():
        if write_num1 < MIN_SINGLE_NUM or write_num1 > MAX_SINGLE_NUM:
            continue
        for write_num2, _ in write_num_dict.items():
            if write_num2 < MIN_SINGLE_NUM or write_num2 > MAX_SINGLE_NUM:
                continue
            combination.append((write_num1, write_num2))
    print('所有字典中笔画的组合：', len(combination), combination)
    return combination


def calDictWugeAfter():
    """
    根据姓，计算的三才五格优秀的配比
    :return:
    """
    return [(3, 14), (4, 14), (4, 7), (11, 20), (11, 4), (3, 17), (3, 7), (11, 14), (19, 12), (11, 10), (4, 17),
            (9, 12), (7, 10), (11, 3), (11, 12)]


def start():
    global global_sancai_wuxing_dict
    global_sancai_wuxing_dict = getSancaiData()
    try:
        # 三才五格计算
        best_wuge_combination = calHaohaoWuge()  # 通过三才五格公式自己算
        # 网站的优秀三才五格配比
        best_dict_combination = calDictWugeAfter()  # 通过字典暴力遍历

        # 结合上面的结果晒出列表
        best_list = []
        for best in best_wuge_combination:
            compare_item = (best[0], best[1])
            if compare_item not in best_dict_combination:
                continue
            best_list.append(best)
        print('综合计算的结果：', len(best_list), best_list)

        sancaiwuge_sel = getSancaiWugeSelection(best_list)
        calSelection(sancaiwuge_sel)

        # 喜用神计算
        # best_xiyongshen_combination = calHaohaoXiyongshen()  # 好好没有超好的结果

        # 个性化计算
        # wife_sel = getMyWifeSelection()
        # calSelection(wife_sel)
    except Exception as e:
        traceback.print_exc()
        print('Have a rest, then continue...')
        print('Error:', str(e))
        time.sleep(5)


if __name__ == '__main__':
    start()
