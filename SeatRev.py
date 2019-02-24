from urllib import request, parse
import ssl
import json
import time


class WrongPasswdError(Exception):
    """
    账号或者密码错误
    """
    pass


class InvalidOperationError(Exception):
    """
    程序执行操作失败，且为服务端的原因
    """
    pass


class TimeSetError(Exception):
    """
    时间设置错误
    """
    pass


class SeatReserve:
    """
    图书馆座位预约插件
    """
    @staticmethod
    def load_config(config_path="config.json"):
        """
        导入config.json中的参数
        """
        try:
            with open(config_path, 'r') as f:
                config = json.loads(f.read())
                return config
        except FileNotFoundError:
            print("找不到config.json文件，请确认它与当前程序在同一文件夹中")

    @staticmethod
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

    @staticmethod
    def is_reasonable_time(start_time, end_time):
        """
        默认开始时间不是now
        :param start_time: 开始时间，整数（分钟）
        :param end_time: 结束时间，整数（分钟）
        :return: Bool
        """
        int_start_time = int(start_time)
        int_end_time = int(end_time)
        if int_end_time <= int_start_time:
            return False
        if int_start_time % 30 != 0 or int_end_time % 30 != 0:
            return False
        if start_time < 480 or end_time > 630:
            return False
        return True

    @staticmethod
    def time_transfer(set_time):
        """
        将“小时：分钟”表示的时间转换为分钟表示
        :param set_time: str {}:{}
        :return: str，minute
        """
        hours, minutes = [int(time_element) for time_element in set_time.split(":")]
        return str(hours * 60 + minutes)

    def __init__(self):
        self.context = ssl._create_unverified_context()
        self.headers = {
            "Host": "seat.lib.whu.edu.cn:8443",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "doSingle/11 CFNetwork/976 Darwin/18.2.0",
            "Accept-Language": "zh-cn",
            "Accept-Encoding": "gzip, deflate"
        }
        self.config_data = self.load_config()
        self.reserve_date, self.is_tomorrow = self.get_reserve_date()  # reserve_date是一个字符串类型
        self.username = self.config_data["username"]
        self.password = self.config_data["password"]
        self.login()
        print("------Log in successfully------")

    def req_with_json(self, url, data=None):
        """
        用于处理返回值为json的请求
        :param data: POST请求中发送的内容
        :param url: string
        :return: dict
        """
        req = request.Request(url, headers=self.headers, data=data)
        response = request.urlopen(req, context=self.context).read().decode("utf-8")
        return json.loads(response)

    def login(self):
        """
            用于模拟自习助手的登陆，从而实现绕过验证码
            :return: token, string 系统用token验证身份
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/auth?username={0}&password={1}".format(self.username,
                                                                                            self.password)
        response = self.req_with_json(url)  # 返回的是string格式
        if response["status"] == "fail":
            raise WrongPasswdError("账号或密码不正确，请修改同目录下config.json中的账号和密码")
        token = response["data"]["token"]
        self.headers["token"] = token  # 自动更新headers，加入token记录登陆信息

    def get_violations(self):
        """
        获得违约记录
        :return: 不知道data的具体形式，反正是个list
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/violations"
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def get_settings(self):
        """
        获得当前图书馆的预约规则
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/settings"
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def get_user_info(self):
        """
        获得用户信息
        :return: dict，包含是否进馆，用户姓名，违约记录等
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/user"
        response = self.req_with_json(url)
        data = response["data"]
        # name = data["name"]
        # status = data["status"]
        # checked_in = data["checkedIn"]
        # reservation_state = data["reservationStatus"]
        # violation_count = data["violationCount"]
        return data

    def get_resevation_info(self):
        """
        查询当前的预约状态
        :return: 如果没有预约，则返回None；如果有，则返回一个seat_id的string，用于取消座位
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/user/reservations"
        response = self.req_with_json(url)
        print(response)
        data = response["data"]
        if not data:
            print("当前没有已预约的座位")
            return None
        rsv_data = data[0]
        reserve_id = rsv_data["id"]
        seat_id = rsv_data["seatId"]
        seat_location = rsv_data["location"]
        start = rsv_data["begin"]
        end = rsv_data["end"]
        status = rsv_data["status"]
        print("当前有一个位置在{}，时间为{}~{}的预约".format(seat_location, start, end))
        return reserve_id, seat_id, status

    def get_history(self):
        """
        获得预约历史
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/history/1/10"
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def get_floor_info(self):
        """
        获得图书馆各个房间的代码
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/free/filters"
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def get_room_info(self, lib_code):
        """
        获得各个分馆的房间信息
        :param lib_code:[1,"信息馆"],[2,"工学分馆"],[3,"医学分馆"],[4,"总馆"]
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/room/stats2/{}".format(lib_code)
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def get_seat_info(self, room_id):
        """
        获取某一roomid下的座位情况
        :param room_id：int
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/room/layoutByDate/{}/{}".format(room_id, self.reserve_date)
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def get_seat_start_time(self, seat_id):
        """
        获取指定座位seat_id的可预约时间
        :param seat_id: int
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/startTimesForSeat/{}/{}".format(seat_id, self.reserve_date)
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def get_seat_end_time(self, seat_id, start_time):
        """
        获取指定座位seat_id从指定开始时间start_time的可用的结束时间
        :param seat_id: int
        :param start_time: int，计算方法为hour(24) * 60 + minute
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/endTimesForSeat/{}/{}/{}".format(seat_id,
                                                                                         self.reserve_date,
                                                                                         start_time)
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def reserve_seat(self, seat_id, start_time, end_time):
        """
        预约座位
        :param seat_id: 所要预约的座位号
        :param start_time: 开始时间，特殊值为“now”
        :param end_time: 结束时间
        :return: 预约的请求号
        """
        if not self.is_reasonable_time(start_time, end_time):
            raise TimeSetError("预约的时间错误，请重新设定预约时间")
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/freeBook"
        raw_data = {
            "t": 1,
            "startTime": start_time,
            "endTime": end_time,
            "seat": seat_id,
            "date": self.reserve_date,
            "t2": 2
        }
        data_to_send = parse.urlencode(raw_data).encode("utf-8")
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
            raise InvalidOperationError("座位预约失败，当前座位可能已被预约，或者这个脚本已失效！")

    def stop_using(self):
        """
        用于释放座位
        {"status":"success","data":null,"message":"已终止使用当前预约","code":"0"}
        :return: dict
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/stop"
        response = self.req_with_json(url)
        data = response["data"]
        return data

    def cancel_seat(self, reserve_id):
        """
        取消预约
        须先通过get_resevation_info函数获得座位的id
        :param reserve_id: int
        :return: None
        """
        url = "https://seat.lib.whu.edu.cn:8443/rest/v2/cancel/{}".format(reserve_id)
        response = self.req_with_json(url)
        if response["status"] == "success":
            print("预约取消成功！")
        else:
            raise InvalidOperationError("取消操作失败，或者这个脚本已失效！")


if __name__ == "__main__":
    rev = SeatReserve()
    start_time_minute = rev.time_transfer("8:30")
    end_time_mintue = rev.time_transfer("9:30")
    seat_id_to_reserve = 11111
    info = rev.reserve_seat(seat_id_to_reserve, start_time_minute, end_time_mintue)
