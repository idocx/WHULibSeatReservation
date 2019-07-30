#############################################################
#                        作者：我.doc
# Github地址：https://github.com/idocx/WHULibSeatReservation
#############################################################

from requests import Session
from json import loads
import utils


class AppRes(Session):
    default_header = {
        "Host": "seat.lib.whu.edu.cn:8443",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "doSingle/11 CFNetwork/976 Darwin/18.2.0",
        "Accept-Language": "zh-cn",
        "Accept-Encoding": "gzip, deflate",
    }
    orgin_host = "https://seat.lib.whu.edu.cn:8443/"

    @staticmethod
    def load_config():
        """
        导入config.json中的参数
        """
        config = utils.config
        return config


    def __init__(self):
        super(AppRes, self).__init__()
        self.headers.update(self.default_header)
        self.config_data = self.load_config()
        self.reserve_date = utils.get_reserve_date()  # reserve_date是一个字符串类型
        self.login()

    def req_with_json(self, url, data=None):
        """
        用于处理返回值为json的请求
        :param data: POST请求中发送的内容
        :param url: string
        :return: dict
        """
        url = self.orgin_host + url
        if data:
            req = self.post(url, data=data)
        else:
            req = self.get(url)
        response = req.text
        return loads(response)

    def login(self):
        """
            用于模拟自习助手的登陆，从而实现绕过验证码
            :return: token, string 系统用token验证身份
        """
        url = "rest/auth?username={0}&password={1}".format(self.config_data["username"], self.config_data["password"])
        response = self.req_with_json(url)
        if response["status"] == "fail":
            raise utils.LoginError("账号或密码不正确，请修改同目录下config.json中的账号和密码")
        token = response["data"]["token"]
        self.headers["token"] = token  # 自动更新headers，加入token记录登陆信息
        print("【APP端登陆成功】")

    def get_resevation_info(self):
        """
        查询当前的预约状态
        :return: 如果没有预约，则返回None；如果有，则返回一个seat_id的string，用于取消座位
        """
        url = "rest/v2/user/reservations"
        response = self.req_with_json(url)
        data = response["data"]
        if not data:
            print("当前没有预约")
            return (None,) * 3
        res_data = data[0]
        res_id = res_data["id"]
        seat_status = res_data["status"]
        seat_id = res_data["seatId"]
        seat_location = res_data["location"]
        start = res_data["begin"]
        end = res_data["end"]
        print("当前有一个位置在{}，时间为{}~{}的预约".format(seat_location, start, end))
        return seat_id, res_id, seat_status

    def reserve_seat(self, seat_id, start_time, end_time):
        """
        预约座位
        :param seat_id: 所要预约的座位号
        :param start_time: 开始时间，特殊值为“now”
        :param end_time: 结束时间
        :return: 预约的请求号
        """
        if not utils.is_reasonable_time(start_time, end_time):
            raise utils.TimeSetError("预约的时间错误，请重新设定预约时间")
        url = "rest/v2/freeBook"
        data_to_send = {
            "t": 1,
            "startTime": start_time,
            "endTime": end_time,
            "seat": seat_id,
            "date": self.reserve_date,
            "t2": 2
        }
        response = self.req_with_json(url=url, data=data_to_send)
        data = response["data"]
        if response["status"] == "success":
            location = data["location"]
            start = data["begin"]
            end = data["end"]
            date = data["onDate"]
            reserve_id = data["id"]
            print("已成功预约了座位{}，时间为{}~{}，日期为{}".format(location, start, end, date))
            return reserve_id
        else:
            print("座位预约失败，当前座位可能已被预约，或者您已经有有效预约！")

    def stop_using(self):
        """
        用于释放座位
        {"status":"success","data":null,"message":"已终止使用当前预约","code":"0"}
        :return: dict
        """
        url = "rest/v2/stop"
        response = self.req_with_json(url)
        print(response["message"])
        if response["status"] != "success":
            return False
        return True

    def cancel_seat(self, reserve_id):
        """
        取消预约
        须先通过get_resevation_info函数获得座位的id
        {'status': 'success', 'data': None, 'message': '', 'code': '0'}
        :param reserve_id: int
        :return: True/False
        """
        url = "rest/v2/cancel/{}".format(reserve_id)
        response = self.req_with_json(url)
        if response["status"] == "success":
            print("取消预约成功")
            return True
        print("取消预约失败")
        return False


if __name__ == "__main__":
    res = AppRes()
    res.get_resevation_info()
    # seat_id, res_id, seat_status = res.get_resevation_info()
    # if seat_status == "RESERVE":
    #     assert res.cancel_seat(res_id)  # 取消预约
    # else:
    #     assert res.stop_using()  # 释放座位
    # res.reserve_seat(seat_id, 840, 1290)
