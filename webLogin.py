from urllib import request, parse
import random
from io import BytesIO
import base64
import json
import Captcha
import re
import utils


class WebRes:
    """
    实现网页端预约
    """
    def __init__(self):
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
        self.headers["Cookie"] += ";" + self.get_jsessionid()  # 获取cookie，并且写入头文件
        self.synchronizer_token = self.get_synchronizer_token()  # 获取token，这个在登陆的时候要用
        self.authid = self.check_captcha()  # 识别正确验证码后，系统会返回一个token，表明你已经验证成功了
        self.config = self.load_config()
        self.reserve_date = utils.get_reserve_date()
        self.login()

    @staticmethod
    def load_config():
        """
        加载相关配置文件，并且对其进行必要的转换
        :param room_code_path:
        :return:
        """
        try:
            config = utils.config

            config["lib"] = utils.lib_code[config["lib"]]
            config["startmin"] = utils.time_transfer(config["starttime"])
            config["endmin"] = utils.time_transfer(config["endtime"])

            if not utils.is_reasonable_time(config["startmin"], config["endmin"]):
                raise utils.TimeSetError("预约的时间错误，请重新设定预约时间")

            config["window"] = utils.window_code[config["window"]]
            config["power"] = utils.power_code[config["power"]]

            config["room"] = utils.room_code[config["room"]]
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
        headers["Accept"] = "text/html,application/xhtml+xml,application/" \
                            "xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        url = "https://seat.lib.whu.edu.cn/login?targetUri=%2F"
        req = request.Request(url, headers=self.headers)
        response = request.urlopen(req).read().decode("utf-8")

        token = re.search('(?<=name="SYNCHRONIZER_TOKEN" value=").+?(?=")', response).group()  # 利用正则表达式解析网页

        return token

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
        captcha_url = "https://seat.lib.whu.edu.cn/captchaImg?" \
                      "token={}&r={}".format(token, random.random())
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
        url = "https://seat.lib.whu.edu.cn/checkCaptcha?" \
              "a={}%3D&token={}&userId=HTTP/1.1".format(pos_data.decode('utf-8'), token)
        req = request.Request(url, headers=headers)
        response = request.urlopen(req).read().decode("utf-8")
        response = json.loads(response)
        if response["status"] != "OK":
            token = self.check_captcha()
        return token

    def login(self):
        """
        登陆程序，只要把该发的都发过去就行了，还有这里的Token更新了
        :return:
        """
        url = "https://seat.lib.whu.edu.cn/auth/signIn"
        headers = self.headers
        headers["Cache-Control"] = "max-age=0"
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "text/html,application/xhtml+xml,application/" \
                            "xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
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

        # 要姓名是为了验证成功登陆
        if re.search(r'(?<=<strong>).+?(?=</strong>)', response).group() != self.config["name"]:
            raise utils.LoginError("登陆失败")

        synchronizer_token = re.search('(?<=name="SYNCHRONIZER_TOKEN" value=").+?(?=")', response).group()
        self.synchronizer_token = synchronizer_token

        print("------网页端登陆成功------")

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
        """
        对当前的空座位进行扫描
        :return: 返回空闲的座位的id
        """
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

    def res_seat(self, target_seat):
        """
        :param target_seat: 要预约的座位id，是一个整形
        :return: bool value，便于循环
        """
        url = "https://seat.lib.whu.edu.cn/selfRes"
        headers = self.headers
        headers["Referer"] = "https://seat.lib.whu.edu.cn/"

        raw_data = {
            "SYNCHRONIZER_TOKEN": self.synchronizer_token,
            "SYNCHRONIZER_URI": "/",
            "date": self.reserve_date,
            "seat": target_seat,
            "start": self.config["startmin"],
            "end": self.config["endmin"],
            "authid": -1,
        }

        data_to_send = parse.urlencode(raw_data).encode("utf-8")
        headers["Content-Length"] = str(len(data_to_send))
        req = request.Request(url, headers=headers, data=data_to_send)
        response = request.urlopen(req).read().decode("utf-8")

        try:
            if re.search(r'(?<=状&nbsp;&nbsp;&nbsp;&nbsp;态 ： </em>).+?(?=</dd>)', response).group() != "预约":
                raise AttributeError
        except AttributeError:
            print("预约失败，可能是座位已经被预约或您当前已有预约")
            return False

        location = re.search(r'(?<=<em>位&nbsp;&nbsp;&nbsp;&nbsp;置 ： </em>).+?(?=</dd>)', response).group()
        time = re.search(r'(?<=<em>时&nbsp;&nbsp;&nbsp;&nbsp;间 ： </em>).+?(?=</dd>)', response).group()

        print("\n"
              "------预约成功------\n",
              "位置：{0}\n".format(location),
              "时间：{0}~{1}".format(*time.split("-")))
        return True


if __name__ == "__main__":
    pass
