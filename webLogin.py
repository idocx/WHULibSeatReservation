#############################################################
#                        作者：我.doc
# Github地址：https://github.com/idocx/WHULibSeatReservation
#############################################################

from requests import Session
import random
from base64 import b64encode
import json
import re
import utils
import captcha_win


class WebRes(Session):
    """
    实现网页端预约
    """
    default_header = {
        "Host": "seat.lib.whu.edu.cn",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/72.0.3626.121 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    orgin_host = "https://seat.lib.whu.edu.cn/"

    @staticmethod
    def load_config(config):
        """
        加载相关配置文件，并且对其进行必要的转换
        :return:
        """
        config["room"] = utils.room_code[config["lib"]][config["room"]]  # 先取房间再取场馆
        config["lib"] = utils.lib_code[config["lib"]]
        config["startmin"] = utils.time_transfer(utils.start_time_list[config["starttime"]])
        config["endmin"] = utils.time_transfer(utils.end_time_list[config["endtime"]])
        config["window"] = utils.window_code[config["window"]]
        config["power"] = utils.power_code[config["power"]]
        return config

    def __init__(self, config_file, parent=None):
        super(WebRes, self).__init__()
        self.parent = parent
        self.cap_win = None
        self.headers.update(self.default_header)
        self.config = self.load_config(config_file)
        self.get_home_page()
        self.synchronizer_token = self.get_synchronizer_token()  # 获取token，这个在登陆的时候要用
        self.authid = self.check_captcha()  # 识别正确验证码后，系统会返回一个token，表明你已经验证成功了
        self.login()
        self.reserve_date = utils.get_reserve_date()

    def get_home_page(self):
        """
        访问主界面，获得cookie
        :return: None
        """
        url = self.orgin_host
        self.get(url)

    def get_synchronizer_token(self):
        """
        获取一个token，用作身份识别
        :return: synchronizer token
        """
        self.headers.update({"Origin": self.orgin_host})
        url = self.orgin_host + "login?targetUri=%2F"
        response = self.get(url).text
        self.headers.update({"Referer": url})

        try:
            token = re.search(r'(?<=name="SYNCHRONIZER_TOKEN" value=").+?(?=")', response).group()
        except AttributeError:
            raise utils.LoginError("无法访问网页，请检查当前网络状态；或者图书馆网站正在维护")

        return token

    def get_captcha(self):
        """
        获取并且调用打开验证码的窗口，供用户识别
        :return:
        """
        url = self.orgin_host + "captcha"
        response = self.get(url).text
        response = json.loads(response)
        str_data = response["data"]
        token = response["token"]
        return self.open_captcha(str_data, token), token

    def open_captcha(self, cap_text, token):
        """
        打开验证码的窗口
        :param cap_text: 所要求点选的字
        :param token: 请求图片的token
        :return: 经过base64加密的坐标信息
        """
        captcha_url = self.orgin_host + "captchaImg?token={}&r={}".format(token, random.random())
        img = self.get(captcha_url).content
        self.cap_win = captcha_win.CaptchaWin(cap_text, img, parent=self.parent)
        self.cap_win.exec()
        pos = self.cap_win.get_pos()
        if len(pos) < 3:
            raise Exception("程序意外终止，请重新启动")
        pos = json.dumps(pos)
        return b64encode(bytes(pos, encoding="utf-8"))

    def check_captcha(self):
        """
        把识别好的验证码数据发出，如果不正确，就再发一次，直至成功为止
        :return: 验证后的token
        """
        pos_data, token = self.get_captcha()
        url = self.orgin_host + "checkCaptcha?a={}%3D&token={}&userId=HTTP/1.1".format(pos_data.decode('utf-8'), token)
        response = self.get(url).text
        response = json.loads(response)
        if response["status"] != "OK":
            token = self.check_captcha()
        return token

    def login(self):
        """
        登陆程序，只要把该发的都发过去就行了，还有这里的Token更新了
        :return:
        """
        url = self.orgin_host + "auth/signIn"
        data_to_send = {
            "SYNCHRONIZER_TOKEN": self.synchronizer_token,
            "SYNCHRONIZER_URI": "/login",
            "username": self.config["username"],
            "password": self.config["password"],
            "authid": self.authid,
        }
        response = self.post(url, data=data_to_send).text
        self.headers.update({
            "Referer": self.orgin_host
        })

        if not re.search(r'(?<=<a id="btnStop" href="#" action="stopUsing">).+?(?=</a>)', response):
            raise utils.LoginError("登陆失败")

        synchronizer_token = re.search('(?<=name="SYNCHRONIZER_TOKEN" value=").+?(?=")', response).group()

        self.synchronizer_token = synchronizer_token
        print("【网页端登陆成功】")

    def free_search(self):
        """
        对当前的空座位进行搜索
        :return: 返回空闲的座位的id list
        """
        url = self.orgin_host + "freeBook/ajaxSearch"
        if not utils.is_reasonable_time(self.config["startmin"], self.config["endmin"]):
            raise utils.TimeSetError("时间设置不正确，请重新设置")
        data_to_send = {
            "onDate": self.reserve_date,
            "building": self.config["lib"],
            "room": self.config["room"],
            "hour": "null",
            "startMin": self.config["startmin"],
            "endMin": self.config["endmin"],
            "power": self.config["power"],
            "window": self.config["window"],
        }
        response = self.post(url, data=data_to_send).text

        seat_available = re.findall(r'(?<=id=\\"seat_).+?(?=\\")', response)
        seat_available = [int(i) for i in seat_available]
        return seat_available

    def res_seat(self, target_seat):
        """
        :param target_seat: 要预约的座位id，是一个int类型
        :return: bool value，便于循环搜索
        """
        url = self.orgin_host + "selfRes"
        data_to_send = {
            "SYNCHRONIZER_TOKEN": self.synchronizer_token,
            "SYNCHRONIZER_URI": "/",
            "date": self.reserve_date,
            "seat": target_seat,
            "start": self.config["startmin"],
            "end": self.config["endmin"],
            "authid": -1,
        }
        response = self.post(url, data=data_to_send).text

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
