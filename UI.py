#############################################################
#                        作者：我.doc                        #
# Github地址：https://github.com/idocx/WHULibSeatReservation #
#       个人网站：https://www.chemhy.design                  #
#############################################################

# 插件的用户界面
import tkinter as tk
from tkinter import ttk
import json
import webLogin
import time
import utils
import random
import appLogin


def get_index(target_element, data_list):
    """
    在元组中查找索引，用于初始化下拉菜单时显示之前配置文件中的值
    :param target_element: 目标元素
    :param data_list: 所要查找的元组
    :return: int，元组中的索引，如果没有，就默认为0
    """
    try:
        target_index = data_list.index(target_element)

    except ValueError:
        target_index = 0

    return target_index


# 图形界面
class Interface:
    def __init__(self):
        # 读取相关配置文件
        self.config = utils.config
        self.room_index = utils.room_index

        # 加载默认值
        self.building_select = self.config["lib"]
        self.room_select = self.config["room"]
        self.start_time_select = self.config["starttime"]
        self.end_time_select = self.config["endtime"]
        self.window_select = self.config["window"]
        self.power_select = self.config["power"]

        # 建立根窗口
        self.interface = tk.Tk()
        self.interface.title("WHU图书馆预约助手")
        self.interface.geometry("750x280+500+300")

        # 分馆选项
        self.building = tk.Label(self.interface, text='分馆')
        self.building.grid(row=0, column=0, ipady=20, ipadx=50)
        self.building_cmb = ttk.Combobox(self.interface)
        building_list = ("不限场馆", "总馆", "信息分馆", "工学分馆", "医学分馆")
        self.building_cmb["values"] = building_list
        self.building_cmb.bind("<<ComboboxSelected>>", self.get_room_info)
        self.building_cmb.current(get_index(self.building_select, building_list))
        self.building_cmb.grid(row=0, column=1, ipadx=20)

        # 房间选项
        self.room = tk.Label(self.interface, text='房间')
        self.room.grid(row=1, column=0, ipady=20, ipadx=50)
        self.room_cmb = ttk.Combobox(self.interface)
        self.room_cmb.bind("<<ComboboxSelected>>", self.get_room_select)
        room_list = self.room_index[self.building_select]
        self.room_cmb["values"] = room_list
        self.room_cmb.current(get_index(self.room_select, room_list))
        self.room_cmb.grid(row=1, column=1, ipadx=20)

        # 开始时间
        self.start_time = tk.Label(self.interface, text='开始时间')
        self.start_time.grid(row=0, column=2, ipady=20, ipadx=50)
        self.start_time_cmb = ttk.Combobox(self.interface)

        self.start_time_cmb["values"] = utils.start_time_list
        self.start_time_cmb.current(get_index(self.start_time_select, utils.start_time_list))
        self.start_time_cmb.bind("<<ComboboxSelected>>", self.get_start_time_select)
        self.start_time_cmb.grid(row=0, column=3, ipadx=20)

        # 结束时间
        self.end_time = tk.Label(self.interface, text='结束时间')
        self.end_time.grid(row=1, column=2, ipady=20, ipadx=50)
        self.end_time_cmb = ttk.Combobox(self.interface)
        self.end_time_cmb["values"] = utils.end_time_list
        self.end_time_cmb.current(get_index(self.end_time_select, utils.end_time_list))
        self.end_time_cmb.bind("<<ComboboxSelected>>", self.get_end_time_select)
        self.end_time_cmb.grid(row=1, column=3, ipadx=20)

        # 是否靠窗
        self.window = tk.Label(self.interface, text='靠窗')
        self.window.grid(row=2, column=0, ipady=20, ipadx=50)
        self.window_cmb = ttk.Combobox(self.interface)
        self.window_cmb.bind("<<ComboboxSelected>>", self.get_window_select)
        window_list = ("不限靠窗", "靠窗", "不靠窗", )
        self.window_cmb["values"] = window_list
        self.window_cmb.current(get_index(self.window_select, window_list))
        self.window_cmb.grid(row=2, column=1, ipadx=20)

        # 是否有电源
        self.power = tk.Label(self.interface, text='电源')
        self.power.grid(row=2, column=2, ipady=20, ipadx=50)
        self.power_cmb = ttk.Combobox(self.interface)
        self.power_cmb.bind("<<ComboboxSelected>>", self.get_window_select)
        power_list = ("不限电源", "有电源", "无电源", )
        self.power_cmb["values"] = power_list
        self.power_cmb.current(get_index(self.power_select, power_list))
        self.power_cmb.grid(row=2, column=3, ipadx=20)

        # 空白占位
        self.blank_area = tk.Label(self.interface, text=' ')
        self.blank_area.grid(row=3, column=1, ipady=0, ipadx=0)

        # 释放操作按钮
        self.release = tk.Button(self.interface, text="释放再预约", command=self.do_release)
        self.release.grid(row=4, column=0, ipadx=30, ipady=0, columnspan=3, sticky=tk.N)

        # 预约操作按钮
        self.res = tk.Button(self.interface, text="预约", command=self.start_res)
        self.res.grid(row=4, column=2, ipadx=50, ipady=0, columnspan=3, sticky=tk.N)

        # 预留的状态Label
        self.res_status = None

        # 显示窗口
        self.interface.mainloop()

    def get_room_info(self, *args):
        """
        记录选择的分馆，弹出相应馆的房间
        :param args: 没啥用，不加会报错
        :return: None
        """
        self.building_select = self.building_cmb.get()
        self.room_cmb["values"] = self.room_index[self.building_select]
        self.room_cmb.current(0)
        self.interface.update()

    def get_room_select(self, *args):
        """
        记录选择的房间
        :param args:
        :return:
        """
        self.room_select = self.room_cmb.get()

    def get_start_time_select(self, *args):
        """
        记录选择的开始时间
        :param args:
        :return:
        """
        self.start_time_select = self.start_time_cmb.get()

    def get_end_time_select(self, *args):
        """
        记录选择的结束时间
        :param args:
        :return:
        """
        self.end_time_select = self.end_time_cmb.get()

    def get_window_select(self, *args):
        """
        记录是否靠窗
        :param args:
        :return:
        """
        self.window_select = self.window_cmb.get()

    def get_power_select(self, *args):
        """
        记录是否需要电源
        :param args:
        :return:
        """
        self.power_select = self.power_cmb.get()

    def save_config(self):
        """
        在开始预约前，先保存配置
        :return:
        """

        # 更改相应的值
        self.config["lib"] = self.building_select
        self.config["room"] = self.room_select
        self.config["starttime"] = self.start_time_select
        self.config["endtime"] = self.end_time_select
        self.config["window"] = self.window_select
        self.config["power"] = self.power_select

        with open("config.json", "w", encoding="utf-8") as configure:
            json.dump(self.config, configure, ensure_ascii=False)

        # 显示预约进行状态（没啥用）
        self.res_status = tk.Label(self.interface, text='开始尝试预约')
        self.res_status.grid(row=5, column=2, ipady=10, ipadx=20, columnspan=3)
        self.interface.update()

    @staticmethod
    def web_search_loop():
        """
        搜索座位的主函数
        :return:
        """
        count = 1
        is_success = 0
        web_res = webLogin.WebRes()

        # 判断是否进入等待模式
        time.sleep(utils.get_rest_time())

        while not is_success:
            seat_list = web_res.free_search()
            while not seat_list:
                print("【第{0}次搜索】目前没有空闲位置".format(count))
                time.sleep(utils.interval_time + random.randint(0, 2))
                seat_list = web_res.free_search()
                count += 1

            print("【第{0}次搜索】发现空闲位置，尝试预约".format(count))

            time.sleep(1)

            seat = random.choice(seat_list)
            is_success = web_res.res_seat(seat)
            count += 1

    @staticmethod
    def release_seat():
        """
        取消预约在预约的主函数
        :return:
        """
        # 登陆web端
        web_res = webLogin.WebRes()

        # 登陆app端
        app_res = appLogin.AppRes()

        seat_id, res_id, seat_status = app_res.get_resevation_info()  # 获取预约信息
        assert seat_id
        print("开始尝试重新预约")
        if seat_status == "RESERVE":
            assert app_res.cancel_seat(res_id)  # 取消预约
        else:
            assert app_res.stop_using()  # 释放座位

        web_res.res_seat(seat_id)  # 尝试通过网页端重新预约

    def start_res(self):
        """
        调用./webLogin中的函数进行座位查找
        :return:
        """
        self.save_config()
        time.sleep(0.7)
        self.interface.destroy()  # 关闭页面，不然会产生一些错误
        self.web_search_loop()  # 开始循环

    def do_release(self):
        self.res_status = tk.Label(self.interface, text='开始尝试释放预约')
        self.res_status.grid(row=5, column=0, ipady=10, ipadx=20, columnspan=3)
        self.interface.update()
        time.sleep(0.7)
        self.interface.destroy()  # 关闭页面，不然会产生错误
        self.release_seat()


if __name__ == "__main__":
    Interface()
