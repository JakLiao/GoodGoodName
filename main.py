#!/usr/bin/python
# -*-coding:utf-8-*-
__author__ = 'HaoHao de Father'
import random
import traceback
from collections import defaultdict
from conf import config, constants
from conf.config import LAST_NAME, MIN_SINGLE_NUM, MAX_SINGLE_NUM, SELECTED_SANCAI, SELECTED_XITONGSHEN
import utils
import time
from data import self_wuxing_dict as w

g_sancai_wuxing_dict = {}
g_baijiaxing_dict = {}  # 百家姓最佳搭配
g_selected_write_dict = {
    '水': w.shui_dict,
    '火': w.huo_dict,
    '木': w.mu_dict,
    '金': w.jin_dict,
    '土': w.tu_dict
}
g_last_name_write_num = utils.FULL_WORD_COUNT_DICT[config.LAST_NAME]


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
            name_list.append(LAST_NAME + mid + last)
    for mid in five_hang_huo:
        for last in five_hang_mu:
            name_list.append(LAST_NAME + mid + last)
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
    :param verbose 展示参考的笔画数量
    :return:
    """
    write_num_set = set()  # 展示参考的笔画数量
    name_num_backup_list = utils.getWordWriteCountWugeCombination()

    # 结果总格和外格计算
    best_wuge_combination = []
    for (mid_num, last_num) in name_num_backup_list:
        tian_ge = g_last_name_write_num + 1
        zong_ge = g_last_name_write_num + mid_num + last_num
        ren_ge = g_last_name_write_num + mid_num
        di_ge = mid_num + last_num
        wai_ge = zong_ge - ren_ge + 1
        # FIXME 这里真的有必要把总格和外格过滤？？
        if zong_ge not in constants.best_num_set or wai_ge not in constants.best_num_set:
            continue
        # 计算三才
        sancai, sancai_result, sancai_evaluate = calHoahaoSancai(tian_ge, ren_ge, di_ge)
        if '凶' in sancai_result or sancai_result == constants.RESULT_UNKNOWN:
            # print('过滤判断为凶或未知的三才：', sancai, sancai_result)
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
        print('**好好五格名字笔画数量：', len(best_wuge_combination), '\n笔画组合如下所示：')
        for o in best_wuge_combination:
            print('\t', o)
        print('\t名字中乾隆字典笔画包括：', output_num_list)

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
    if sancai in g_sancai_wuxing_dict:
        data = g_sancai_wuxing_dict[sancai]
        return sancai, data['result'], data['evaluate']
    else:
        return sancai, constants.RESULT_UNKNOWN, None


def calHaohaoXiyongshen():
    """
    方法三：
    五行（喜用神）最适合的计算
    计算你名字的五行与笔划数量的时候，按照乾隆字典计算
    12345对应水火木金土，67890也对应水火木金土，12345为阳，67890为阴，
    故甲阳木3，乙阴木8，丙阳火2，丁阴火7，庚阳金4，辛阴金9，壬阳水1，癸阴水6，戊阳土5，己阴土0
    参考：https://www.lnka.cn/article/topic2285.html
    :return:
    """
    if not SELECTED_XITONGSHEN:
        print('必须先在config.py中配置喜用神')
        return None
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


def calSelection(name_list, is_skip_tested=False):
    """
    从选出的名字列表中，请求起名网站查看分数
    :param name_list:
    :param is_skip_tested:  是否跳过已经测试过的名字不重复测试
    :return:
    """
    if not config.true_request:
        return
    already_tested_dict = {}
    if is_skip_tested:
        already_tested_dict = utils.getTestedDict()
    for name in name_list:
        if name in already_tested_dict:
            continue
        utils.getScore(name)
        # 按照正常用户的速度来访问，避免请求太快被封掉了
        time.sleep(random.randint(4, 6))


def getWriteNumDict():
    """
    根据五行找字典中的字。如果配置为None则全部都选。
    :return:
    """
    if SELECTED_XITONGSHEN:
        return g_selected_write_dict[SELECTED_XITONGSHEN]
    else:
        write_num_dict = defaultdict(list)
        for _, wdict in g_selected_write_dict.items():
            for num, word_list in wdict.items():
                write_num_dict[num] += word_list
        return write_num_dict


def getSancaiWugeSelection(best_combination):
    """
    通过三才五格算出的笔画数，找出匹配的名字清单
    :param best_combination:
    :return:
    """
    write_num_dict = getWriteNumDict()
    name_set = set()
    for best in best_combination:
        mid_write_num = best[0]
        last_write_num = best[1]
        if mid_write_num not in write_num_dict or last_write_num not in write_num_dict:
            # 假如找不到这个笔画，跳过处理
            continue
        mid_selection_list = write_num_dict[mid_write_num]
        last_selection_list = write_num_dict[last_write_num]

        if config.debug:
            # 仅仅测试下笔画配比
            name_set.add(LAST_NAME + mid_selection_list[0] + last_selection_list[0])
        else:
            # 所有名字都测试下
            for m in mid_selection_list:
                for l in last_selection_list:
                    name_set.add(LAST_NAME + m + l)  # 反过来的话人格和地格就不对了
    print('三才五格待测试名字列表：', len(name_set), name_set)
    return name_set


def calFullDictWuge():
    """
    方法七：
    通过字典枚举暴力遍历所有组合，有324种组合

    运算后结果看name.txt, 笔画列表放入 calDictWugeAfter()， 方便后续快速运算
    :return:
    """
    combination = []
    write_num_dict = getWriteNumDict()
    for write_num1, _ in write_num_dict.items():
        if write_num1 < MIN_SINGLE_NUM or write_num1 > MAX_SINGLE_NUM:
            continue
        for write_num2, _ in write_num_dict.items():
            if write_num2 < MIN_SINGLE_NUM or write_num2 > MAX_SINGLE_NUM:
                continue
            combination.append((write_num1, write_num2))
    print('所有字典中笔画的组合：', len(combination), combination)
    return combination


def getLastNameWuge(lastname):
    return g_baijiaxing_dict[lastname] if lastname in g_baijiaxing_dict else []
    # return [(3, 14), (4, 14), (4, 7), (11, 20), (11, 4), (3, 17), (3, 7), (11, 14), (19, 12), (11, 10), (4, 17),
    #         (9, 12), (7, 10), (11, 3), (11, 12)]


def mainBestSancaiwuge():
    """
    综合计算
    三才五格 自己算的和网站算的求交集
    :return:
    """
    # 三才五格计算
    best_wuge_combination = calHaohaoWuge()  # 通过三才五格公式自己算的理论值
    # 根据姓氏优秀三才五格配比
    best_dict_combination = getLastNameWuge(config.LAST_NAME)

    # 结合上面的结果晒出列表
    best_list = []
    for best in best_wuge_combination:
        compare_item = (best[0], best[1])
        if compare_item not in best_dict_combination:
            continue
        best_list.append(best)
    if best_list:
        print('综合计算的结果，数量{}, 组合{}'.format(len(best_list), best_list))
    else:
        # 如果实在匹配不到，用理论值替代
        best_list = best_wuge_combination
        print('没有得到最好的三才五格配置，建议适当放宽constants中good_num_list和bad_num_list的要求。')

    sancaiwuge_sel = getSancaiWugeSelection(best_list)
    calSelection(sancaiwuge_sel)


def calFixWord(again=False):
    """
    名字中固定一个字，再取名
    :return:
    """
    fix_write_word = config.fix_write_word
    fix_write_num = utils.FULL_WORD_COUNT_DICT[fix_write_word]
    write_num_dict = getWriteNumDict()

    write_num_list = []
    name_set = set()
    for num in range(MIN_SINGLE_NUM, MAX_SINGLE_NUM + 1):
        if again:
            if (fix_write_num, num) not in config.my_write_num_list:
                continue

        # 固定名字第一个
        write_num_list.append((fix_write_num, num))
        last_write_num = num
        if last_write_num not in write_num_dict:
            continue
        last_selection = write_num_dict[last_write_num]
        if config.debug:
            # 仅仅测试下笔画配比
            name_set.add(LAST_NAME + fix_write_word + last_selection[0])
        else:
            # 所有名字都测试下
            for l in last_selection:
                name_set.add(LAST_NAME + fix_write_word + l)

    for num in range(MIN_SINGLE_NUM, MAX_SINGLE_NUM + 1):
        if again:
            if (num, fix_write_num) not in config.my_write_num_list:
                continue
        # 固定名字第二个
        write_num_list.append((num, fix_write_num))
        mid_write_num = num
        if mid_write_num not in write_num_dict:
            continue
        mid_selection = write_num_dict[mid_write_num]

        if config.debug:
            # 仅仅测试下笔画配比
            name_set.add(LAST_NAME + mid_selection[0] + fix_write_word)
        else:
            # 所有名字都测试下
            for m in mid_selection:
                name_set.add(LAST_NAME + m + fix_write_word)

    print('待测试的名字笔画列表：', len(write_num_list), write_num_list)
    print('待测试的名字列表：', len(name_set), name_set)
    calSelection(name_set)


def start():
    global g_sancai_wuxing_dict
    global g_baijiaxing_dict
    g_sancai_wuxing_dict = utils.getSancaiData()
    g_baijiaxing_dict = utils.getBaijiaxingData()
    try:
        # 适用于普遍的情况下
        mainBestSancaiwuge()

        # 适用于姓名第二个字根据族谱的情况，或者孩子父母有个字特别喜欢的情况
        # calFixWord(again=True)
    except Exception as e:
        traceback.print_exc()
        print('Have a rest, then continue...')
        print('Error:', str(e))
        time.sleep(5)


if __name__ == '__main__':
    start()
