#############################################################
#                        作者：我.doc                        #
# Github地址：https://github.com/idocx/WHULibSeatReservation #
#############################################################


from requests import Session
import random
from io import BytesIO
from base64 import b64encode
import json
import re
import utils
from tkinter import Tk, Label
from PIL import Image, ImageTk


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
    def load_config():
        """
        加载相关配置文件，并且对其进行必要的转换
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

        except AttributeError:
            print("房间名称设置有误，请检查config.json文件")
        except KeyError:
            print("分馆名称设置有误，请检查config.json文件")

    def __init__(self):
        super(WebRes, self).__init__()
        self.headers.update(self.default_header)
        self.config = self.load_config()
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
            raise utils.LoginError("无法访问网页，请检查当前网络状态")

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

    def open_captcha(self, str_data, token):
        """
        打开验证码的窗口
        :param str_data: 所要求点选的字
        :param token: 请求图片的token
        :return: 经过base64加密的坐标信息
        """
        captcha_url = self.orgin_host + "captchaImg?token={}&r={}".format(token, random.random())
        response = self.get(captcha_url).content

        with BytesIO(response) as img:
            cap_win = Captcha(img, str_data)
            pos = cap_win.get_pos()
            if not pos:
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

        try:
            re.search(r'(?<=<a id="btnStop" href="#" action="stopUsing">).+?(?=</a>)', response)
        except AttributeError:
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


class Captcha(Tk):
    def __init__(self, img, string):
        super(Captcha, self).__init__()
        self.pos = []
        self.title("验证码")
        self.geometry("+500+300")

        img = Image.open(img)
        self.img = ImageTk.PhotoImage(img)

        self.cap_label = Label(self, image=self.img)
        self.cap_label.bind("<Button-1>", self.callback)
        self.cap_label.pack()

        self.str_label = Label(self, text='请依次选择图中的"{}"，"{}"，"{}"'.format(*string[:3]))
        self.str_label.pack()

        self.mainloop()

    def callback(self, event):
        x = event.x
        y = event.y
        self.pos.append(
            {"x": x, "y": y}
        )
        # 长度到3时，就会自己关掉
        if len(self.pos) == 3:
            self.destroy()

    def get_pos(self):
        """
        获取位置坐标，供主程序调用
        :return: dict
        """
        return self.pos


if __name__ == "__main__":
    web_res = WebRes()
    seat_list = web_res.free_search()
