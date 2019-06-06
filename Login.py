from urllib import request, parse
import random
from io import BytesIO
import base64
import json
import Captcha
import time
import re

lib_code = {
    "不限场馆": "null",
    "信息分馆": 1,
    "工学分馆": 2,
    "医学分馆": 3,
    "总馆": 4
}


def is_reasonable_time(start_time, end_time):
    """
    默认开始时间不是now
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
    :param set_time: str {}:{}
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
    is_tomorrow = False
    if (hour * 60 + minute) >= 1365:  # 如果时间超过22:45，则对当前日期自动加一
        time_in_sec += 86400
        is_tomorrow = True
    exact_time = time.localtime(time_in_sec)
    date = (exact_time[i] for i in range(3))
    return "{0}-{1:02}-{2:02}".format(*date), is_tomorrow


class TimeSetError(Exception):
    """
    时间设置错误
    """
    pass


class LoginError(Exception):
    """
    登陆失败
    """
    pass


class WHUSeatRev:
    def __init__(self):
        self.islogin = False
        self.headers = {
            "Host": "seat.lib.whu.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/72.0.3626.121 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": "_ga=GA1.3.1294194637.1547733807"
        }
        self.headers["Cookie"] += ";" + self.get_jsessionid()
        self.synchronizer_token = self.get_synchronizer_token()
        self.authid = self.check_captcha()
        self.config = self.load_config("config.json", "room_code.json")
        self.reserve_date, self.is_tomorrow = get_reserve_date()
        self.login()

    @staticmethod
    def load_config(config_path="config.json", room_code_path="room_code.json"):
        try:
            with open(config_path, 'r') as configure:
                config = json.loads(configure.read())

            config["lib"] = lib_code[config["lib"]]
            config["startmin"] = time_transfer(config["starttime"])
            config["endmin"] = time_transfer(config["endtime"])
            if not is_reasonable_time(config["startmin"], config["endmin"]):
                raise TimeSetError("预约的时间错误，请重新设定预约时间")

            with open(room_code_path, 'r') as room_code:
                config["room"] = json.loads(room_code.read())[config["room"]]
                return config

        except FileNotFoundError:
            print("找不到相关配置文件，请确认它与主程序在同一文件夹中")
        except AttributeError:
            print("房间名称设置有误，请检查config.json文件")
        except KeyError:
            print("分馆名称设置有误，请检查config.json文件")

    def get_jsessionid(self):
        url = "https://seat.lib.whu.edu.cn/"
        req = request.Request(url, headers=self.headers)
        response = request.urlopen(req).info()
        jsession_id = response["Set-Cookie"].split("; ")[0]
        return jsession_id

    def get_synchronizer_token(self):
        self.headers["Origin"] = "https://seat.lib.whu.edu.cn"
        headers = self.headers
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        url = "https://seat.lib.whu.edu.cn/login?targetUri=%2F"
        req = request.Request(url, headers=self.headers)
        response = request.urlopen(req).read().decode("utf-8")
        token = re.search('(?<=name="SYNCHRONIZER_TOKEN" value=").+?(?=")', response).group()
        return token

    def get_captcha_page(self):
        headers = self.headers
        headers["Referer"] = "https://seat.lib.whu.edu.cn/login?targetUri=%2F"
        url = "https://seat.lib.whu.edu.cn/simpleCaptcha/chCaptcha"
        req = request.Request(url, headers=headers)
        request.urlopen(req)

    def get_captcha(self):
        headers = self.headers
        headers["Referer"] = "https://seat.lib.whu.edu.cn/simpleCaptcha/chCaptcha"
        headers["X-Requested-With"] = "XMLHttpRequest"
        url = "https://seat.lib.whu.edu.cn/captcha"
        req = request.Request(url, headers=headers)
        response = request.urlopen(req).read().decode("utf-8")
        response = json.loads(response)
        str_data = response["data"]
        token = response["token"]
        return self.identify_captcha(str_data, token), token

    def identify_captcha(self, str_data, token):
        captcha_url = "https://seat.lib.whu.edu.cn/captchaImg?token={}&r={}".format(token, random.random())
        headers = self.headers
        headers["Accept"] = "image/webp,image/apng,image/*,*/*;q=0.8"
        req = request.Request(captcha_url, headers=headers)
        response = request.urlopen(req).read()

        with BytesIO(response) as img:
            cap_win = Captcha.Id_Captcha(img, str_data)
            pos = cap_win.get_pos()
            assert pos
            pos = json.dumps(pos)
        return base64.b64encode(bytes(pos, encoding="utf-8"))

    def check_captcha(self):
        pos_data, token = self.get_captcha()
        headers = self.headers
        headers["Referer"] = "https://seat.lib.whu.edu.cn/simpleCaptcha/chCaptcha"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        headers["Cache-Control"] = "max-age=0"
        url = "https://seat.lib.whu.edu.cn/checkCaptcha?a={}%3D%3D&token={}".format(pos_data.decode('utf-8'), token)
        req = request.Request(url, headers=headers)
        response = request.urlopen(req).read().decode("utf-8")
        response = json.loads(response)
        if response["status"] != "OK":
            self.check_captcha()
        return token

    def login(self):
        url = "https://seat.lib.whu.edu.cn/auth/signIn"
        headers = self.headers
        headers["Cache-Control"] = "max-age=0"
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        headers["Referer"] = "https://seat.lib.whu.edu.cn/login?targetUri=%2F"
        raw_data = {
            "SYNCHRONIZER_TOKEN": self.synchronizer_token,
            "SYNCHRONIZER_URI": "/login",
            "username": self.config["username"],
            "password": self.config["password"],
            "authid": self.authid,
        }
        data_to_send = parse.urlencode(raw_data).encode("utf-8")
        headers["Content-Length"] = str(len(data_to_send))
        req = request.Request(url, headers=headers, data=data_to_send)
        response = request.urlopen(req).read().decode("utf-8")
        if re.search(r'(?<=<strong>).+?(?=</strong>)', response).group() != self.config["name"]:
            raise LoginError("登陆失败")

        synchronizer_token = re.search('(?<=name="SYNCHRONIZER_TOKEN" value=").+?(?=")', response).group()
        self.synchronizer_token = synchronizer_token

        self.islogin = True
        time_in_sec = time.time()
        exact_time = time.localtime(time_in_sec)
        date = (exact_time[i] for i in range(6))
        print("------登陆成功------\n"
              "登陆时间为{3:02}:{4:02}:{5:02}\n"
              "日期为{0}年{1:02}月{2:02}日".format(*date))

    def get_room(self):
        headers = self.headers
        headers["Referer"] = "https://seat.lib.whu.edu.cn/"
        url = "https://seat.lib.whu.edu.cn/freeBook/ajaxGetRooms"
        raw_data = {
            "id": self.config["lib"]
        }
        data_to_send = parse.urlencode(raw_data).encode("utf-8")
        headers["Content-Length"] = str(len(data_to_send))
        req = request.Request(url, headers=headers, data=data_to_send)
        response = request.urlopen(req).read().decode("utf-8")
        return response

    def free_search(self):
        headers = self.headers
        headers["Referer"] = "https://seat.lib.whu.edu.cn/"
        url = "https://seat.lib.whu.edu.cn/freeBook/ajaxSearch"

        raw_data = {
            "onDate": self.reserve_date,
            "building": self.config["lib"],
            "room": self.config["room"],
            "hour": "null",
            "startMin": self.config["startmin"],
            "endMin": self.config["endmin"],
            "power": self.config["power"],
            "window": self.config["window"],
        }

        data_to_send = parse.urlencode(raw_data).encode("utf-8")
        headers["Content-Length"] = str(len(data_to_send))
        req = request.Request(url, headers=headers, data=data_to_send)
        response = request.urlopen(req).read().decode("utf-8")
        seat_available = re.findall(r'(?<=id=\\"seat_).+?(?=\\")', response)
        seat_available = [int(i) for i in seat_available]
        return seat_available

    def rev_seat(self, seats):
        url = "https://seat.lib.whu.edu.cn/selfRes"
        headers = self.headers
        headers["Referer"] = "https://seat.lib.whu.edu.cn/"

        raw_data = {
            "SYNCHRONIZER_TOKEN": self.synchronizer_token,
            "SYNCHRONIZER_URI": "/",
            "date": self.reserve_date,
            "seat": random.choice(seats),
            "start": self.config["startmin"],
            "end": self.config["endmin"],
            "authid": -1,
        }

        data_to_send = parse.urlencode(raw_data).encode("utf-8")
        headers["Content-Length"] = str(len(data_to_send))
        req = request.Request(url, headers=headers, data=data_to_send)
        response = request.urlopen(req).read().decode("utf-8")

        if re.search(r'(?<=状&nbsp;&nbsp;&nbsp;&nbsp;态 ： </em>).+?(?=</dd>)', response).group() != "预约":
            print("------预约失败------")
            return False

        location = re.search(r'(?<=<em>位&nbsp;&nbsp;&nbsp;&nbsp;置 ： </em>).+?(?=</dd>)', response).group()
        print("\n"
              "------预约成功------\n",
              "位置：{0}\n".format(location),
              "时间：{0}~{1}".format(self.config["starttime"], self.config["endtime"]))
        return True


if __name__ == "__main__":
    count = 1
    is_success = 0
    while not is_success:
        s = WHUSeatRev()
        seat_list = s.free_search()
        while seat_list is None:
            print("【第{0}次搜索】目前没有空闲位置".format(count))
            time.sleep(10)
            seat_list = s.free_search()
            count += 1

        print("【第{0}次搜索】发现空闲位置，尝试预约".format(count))
        time.sleep(5)

        is_success = s.rev_seat(seat_list)
