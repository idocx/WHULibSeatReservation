#############################################################
#                        作者：我.doc                        #
# Github地址：https://github.com/idocx/WHULibSeatReservation #
#       个人网站：https://www.chemhy.design                  #
#############################################################

# 用于存放一些公共函数和常量
import time
import json


# 抢座模式下，每次搜索的时间间隔
interval_time = 1

# 各个场馆的代码
lib_code = {
    "不限场馆": "null",
    "信息分馆": 1,
    "工学分馆": 2,
    "医学分馆": 3,
    "总馆": 4,
}

# 有无电源对应的代码
power_code = {
    "不限电源": "null",
    "有电源": 1,
    "无电源": 0,
}

# 是否靠窗对应的代码
window_code = {
    "不限靠窗": "null",
    "靠窗": 1,
    "不靠窗": 0,
}

# 开始时间列表
start_time_list = ("08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
                   "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
                   "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
                   "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
                   "20:00", "20:30", "21:00", "21:30", "22:00",)

# 结束时间列表
end_time_list = ("08:30", "09:00", "09:30", "10:00", "10:30", "11:00",
                 "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
                 "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
                 "17:30", "18:00", "18:30", "19:00", "19:30", "20:00",
                 "20:30", "21:00", "21:30", "22:00", "22:30",)

# 导入各种配置文件
with open("config.json", "r", encoding="utf-8") as configure:
    config = json.loads(configure.read())

with open("room_index.json", "r", encoding="utf-8") as room_index_file:
    room_index = json.loads(room_index_file.read())

with open("room_code.json", 'r', encoding="utf-8") as room_code_file:
    room_code = json.loads(room_code_file.read())


class TimeSetError(Exception):
    """
    时间设置错误
    """
    pass


class CaptchaError(Exception):
    """
    验证码错误
    """
    pass


class LoginError(Exception):
    """
    登陆失败
    """
    pass


def is_reasonable_time(start_time, end_time):
    """
    默认开始时间不是now，用于判断预约时间是否合法
    :param start_time: 开始时间，整数（分钟）
    :param end_time: 结束时间，整数（分钟）
    :return: Bool
    """
    if end_time <= start_time:
        return False
    if start_time % 30 != 0 or end_time % 30 != 0:
        return False
    if start_time < 480 or end_time > 1350:
        return False
    return True


def time_transfer(set_time):
    """
    将“小时：分钟”表示的时间转换为分钟表示
    :param set_time: str like {}:{}
    :return: str，minute
    """
    hours, minutes = [int(time_element) for time_element in set_time.split(":")]
    return hours * 60 + minutes


def get_reserve_date():
    """
    获取应该预约的日期
    :return: 应该预约的日期的字符串，以及是否为预约第二天的座位
    """
    time_in_sec = time.time()
    hour, minute = time.localtime(time_in_sec)[3:5]

    if (hour * 60 + minute) > 1350:  # 如果时间超过22:30，则对当前日期自动加一，自动预约第二天的座位（非常智能）
        time_in_sec += 86400

    exact_time = time.localtime(time_in_sec)
    date = (exact_time[i] for i in range(3))
    return "{0}-{1:02}-{2:02}".format(*date)


def get_rest_time():
    """
    如果时间在22:30~22:45之间，则会开启等候预约模式
    :return:
    """
    *date, hour, minute, second = time.localtime(time.time())[:6]
    print("登陆时间为{3:02}:{4:02}:{5:02}\n"
          "日期为{0}年{1:02}月{2:02}日".format(*date, hour, minute, second))

    # 计算出时间差
    time_rest = 0
    if 1350 < (hour * 60 + minute) < 1365:
        print("进入等待模式，在22:45将自动开始预约\n")
        time_rest = 2703 - (minute * 60 + second)

    return time_rest
