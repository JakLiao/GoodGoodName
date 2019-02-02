# 强烈建议修改
LAST_NAME = '廖'  # 姓氏
SEX = '女'  # 孩子性别，男 或者 女
year = 2018  # 出生的时间：年
month = 8  # 出生的时间：月
date = 19  # 出生的时间：日
hour = 18  # 出生的时间：小时
minute = 25  # 出生的时间： 分钟

# 选择性修改
MIN_SINGLE_NUM = 2  # 单个字最少笔画过滤
MAX_SINGLE_NUM = 20  # 单个字最多笔画过滤
THRESHOLD_SCORE = 85  # 三才五格测试最低能接受的得分，结果记录在RESULT_FILE
SELECTED_XITONGSHEN = None  # 已知的喜用神，或者次喜用神。None表示没关系。这个喜用神自己在网站查查，选填，填了可能没有最佳匹配结果

# 尽量别改，除非你知道是什么意思
debug = False
my_write_num_list = [(7, 10)]  # 经过第一轮测试后笔画的结果， 自己记录下来
true_request = True  # 真实请求测试
# 名字固定要的字
fix_write_word = '宸'
SELECTED_SANCAI = ['大吉', '中吉']  # 三才中，如果为None就不特意选最好的

# 首先在http://www.qimingzi.net/ 网站提交基本信息，点击开始起名，F12查看请求信息把Cookie复制下来
headers = {"Cookie": "bdshare_firstime=1535117517052; Hm_lvt_4baf75bdd37d2c14c33b580be5423f7f=1535117517,1535367603; "
                     "__tins__5033285=%7B%22sid%22%3A%201535367603157%2C%20%22vd%22%3A%206%2C%20%22expires%22%3A"
                     "%201535369610438%7D; __51cke__=; __51laig__=6; "
                     "Hm_lpvt_4baf75bdd37d2c14c33b580be5423f7f=1535367811; userSurname=%e5%bb%96; userSex=2; "
                     "searchType=report; otherPara=%e5%b9%bf%e4%b8%9c%e7%9c%81%e6%b7%b1%e5%9c%b3%7c10%7c%e6%9c%a8%7c"
                     "%3cb%3e%e4%ba%94%e8%a1%8c%e5%88%86%e6%9e%90%3c%2fb%3e%ef%bc%9a%e5%85%ab%e5%ad%97%e8%bf%87%e7%a1"
                     "%ac%ef%bc%8c%e5%85%ab%e5%ad%97%e5%96%9c%e6%9c%a8%ef%bc%8c%e8%b5%b7%e5%90%8d%e6%9c%80%e5%a5%bd"
                     "%e7%94%a8%e4%ba%94%e8%a1%8c%e5%b1%9e%e6%80%a7%e4%b8%ba%e3%80%8c%3cfont+color%3d0033FF%3e%3cb%3e"
                     "%e6%9c%a8%3c%2fb%3e%3c%2ffont%3e%e3%80%8d%e7%9a%84%e5%ad%97%3cbr%3e; year=2018; month=8; "
                     "date=19; hour=18; minute=25",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0"}
