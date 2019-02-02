from functools import reduce

SANCAI_jixiang = [1, 3, 5, 7, 8, 11, 13, 15, 16, 18, 21, 23, 24, 25, 31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61,
                  63,
                  65, 67, 68, 81]  # 吉祥运暗示数（代表健全,幸福,名誉等）
SANCAI_xiaoji = [6, 17, 26, 27, 29, 30, 38, 49, 51, 55, 58, 71, 73, 75]  # 次吉祥运暗示数（代表多少有些障碍，但能获得吉运）
SANCAI_xiong = [2, 4, 9, 10, 12, 14, 19, 20, 22, 28, 34, 36, 40, 42, 43, 44, 46, 50, 53, 54, 56, 59, 60, 62, 64, 66, 69,
                70,
                72, 74, 76, 77, 78, 79, 80]  # 凶数运暗示数（代表逆境,沉浮,薄弱,病难,困难,多灾等）
SANCAI_wise = [3, 13, 16, 21, 23, 29, 31, 37, 39, 41, 45, 47]  # 首领运暗示数（智慧 ）仁勇全备,立上位,能领导众人）
SANCAI_wealth = [15, 16, 24, 29, 32, 33, 41, 52]  # 财富运暗示数（多钱财,富贵,白手可获巨财）
SANCAI_artist = [13, 14, 18, 26, 29, 33, 35, 38, 48]  # 艺能运暗示数（富有艺术天才，对审美,艺术,演艺,体育有通达之能）
SANCAI_goodwife = [5, 6, 11, 13, 15, 16, 24, 32, 35]  # 女德运暗示数（具有妇德，品性温良，助夫爱子）
SANCAI_death = [21, 23, 26, 28, 29, 33, 39]  # 女性孤寡运暗示数（难觅夫君，家庭不和，夫妻两虎相斗，离婚，严重者夫妻一方早亡）
SANCAI_alone = [4, 10, 12, 14, 22, 28, 34]  # 孤独运暗示数（妻凌夫或夫克妻）
SANCAI_merry = [5, 6, 15, 16, 32, 39, 41]  # 双妻运暗示数
SANCAI_stubbon = [7, 17, 18, 25, 27, 28, 37, 47]  # 刚情运暗示数（性刚固执,意气用事）
SANCAI_gentle = [5, 6, 11, 15, 16, 24, 31, 32, 35]  # 温和运暗示数（性情平和,能得上下信望）

# 可以自己配置觉得好的数字
# 参考好的搭配
refer_good_num_list = [SANCAI_jixiang, SANCAI_xiaoji, SANCAI_wise, SANCAI_wealth, SANCAI_artist, SANCAI_goodwife,
                       SANCAI_merry, SANCAI_gentle]
# 自己设定的好的搭配
good_num_list = [SANCAI_jixiang, SANCAI_xiaoji, SANCAI_wise, SANCAI_wealth, SANCAI_artist, SANCAI_goodwife,
                 SANCAI_merry, SANCAI_gentle]

# 参考坏的搭配
refer_bad_num_list = [SANCAI_xiong, SANCAI_death, SANCAI_alone, SANCAI_stubbon]
# 自己设定的坏的搭配
bad_num_list = [SANCAI_xiong, SANCAI_death, SANCAI_alone]

good_num_set = set(reduce((lambda x, y: x + y), good_num_list, []))
bad_num_set = set(reduce((lambda x, y: x + y), bad_num_list, []))
print('五格好分值:', good_num_set)
print('五格差分值:', bad_num_set)
# 筛选出有好没坏的三才五格
best_num_set = [x for x in good_num_set if x not in bad_num_set]
print('想要的三才五格数字:', best_num_set)

RESULT_UNKNOWN = '结果未知'
