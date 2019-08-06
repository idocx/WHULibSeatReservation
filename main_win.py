from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import utils
import pickle
import threading
from time import sleep
from random import choice, randint
import core_value_code
import webLogin
import appLogin
from ctypes import windll
import logo_rc


def load_config(decode_password=True):
    """
    加载配置文件
    :return: dict::config
    """
    try:
        with open("config", "rb") as config_file:
            config = pickle.load(config_file)
            if decode_password:
                config["password"] = core_value_code.cvc2str(config["password"])  # 对密码进行解码
    except EOFError and FileNotFoundError:
        config = {
            "username": "",
            "password": "",
            "lib": 0,
            "room": 0,
            "starttime": 0,
            "endtime": 0,
            "window": 0,
            "power": 0,
        }
    return config


def save_config(config):
    """
    保存配置文件，采用 极 为 先 进 的核心价值观编码器对密码进行编码
    :param config: dict
    :return: None
    """
    config["password"] = core_value_code.str2cvc(config["password"])
    prev_config = load_config(decode_password=False)
    if prev_config == config:
        return None
    with open("config", "wb") as config_file:
        pickle.dump(config, config_file, protocol=4)
    print("配置文件保存成功")


class MainWin:
    def __init__(self, main_win):
        # 初始化变量
        self.config = load_config()  # 载入配置文件
        self.change_time_thread = self.reserve_seat_thread = None  # 进程变量占位符
        self._web_res = self._app_res = None  # 登陆对象占位符
        self.run_flag = False  # 用于中断进程

        # 设置窗口属性
        main_win.setObjectName("main_win")
        main_win.resize(792, 544)
        main_win.setFixedSize(792, 544)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_win.sizePolicy().hasHeightForWidth())
        main_win.setSizePolicy(size_policy)
        font = QtGui.QFont()
        font.setFamily(utils.font_name)
        font.setPointSize(utils.font_size)
        font.setBold(False)
        font.setWeight(50)
        main_win.setFont(font)
        main_win.setMouseTracking(False)
        main_win.setFocusPolicy(QtCore.Qt.TabFocus)

        # 设置字体
        big_label_font = QtGui.QFont()
        big_label_font.setFamily(utils.font_name)
        big_label_font.setPointSize(utils.font_size+2)

        normal_font = QtGui.QFont()
        normal_font.setFamily(utils.font_name)
        normal_font.setPointSize(utils.font_size)

        console_font = QtGui.QFont()
        console_font.setFamily(utils.console_font_name)
        console_font.setPointSize(utils.font_size+1)

        # 设置图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/LOGO/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        main_win.setWindowIcon(icon)
        main_win.setAutoFillBackground(False)
        main_win.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.main_widget = QtWidgets.QWidget(main_win)
        self.main_widget.setObjectName("main_widget")

        # 右侧LOGO
        self.logo = QtWidgets.QLabel(self.main_widget)
        self.logo.setGeometry(QtCore.QRect(600, 145, 130, 130))
        self.logo.setPixmap(QtGui.QPixmap(":/LOGO/logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")

        # 学号标签
        self.username_label = QtWidgets.QLabel(self.main_widget)
        self.username_label.setGeometry(QtCore.QRect(60, 50, 241, 31))
        self.username_label.setFont(big_label_font)
        self.username_label.setObjectName("username")

        # 密码标签
        self.password_label = QtWidgets.QLabel(self.main_widget)
        self.password_label.setGeometry(QtCore.QRect(330, 50, 241, 31))
        self.password_label.setFont(big_label_font)
        self.password_label.setObjectName("password_label")
        self.password_label.setVisible(False)

        # 学号输入框
        self.username_input = QtWidgets.QLineEdit(self.main_widget)
        self.username_input.setGeometry(QtCore.QRect(126, 53, 180, 25))
        self.username_input.setAutoFillBackground(False)
        self.username_input.setClearButtonEnabled(False)
        self.username_input.setFont(big_label_font)
        self.username_input.setObjectName("username_input")
        self.username_input.setVisible(False)

        # 密码输入框
        self.password_input = QtWidgets.QLineEdit(self.main_widget)
        self.password_input.setGeometry(QtCore.QRect(390, 53, 140, 25))
        self.password_input.setAutoFillBackground(False)
        self.password_input.setClearButtonEnabled(False)
        self.password_input.setFont(big_label_font)
        self.password_input.setObjectName("password_input")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setVisible(False)

        # 确认修改按钮
        self.do_change_button = QtWidgets.QPushButton(self.main_widget)
        self.do_change_button.setGeometry(QtCore.QRect(570, 50, 121, 31))
        self.do_change_button.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.do_change_button.setCheckable(False)
        self.do_change_button.setAutoDefault(False)
        self.do_change_button.setDefault(False)
        self.do_change_button.setFlat(False)
        self.do_change_button.setFont(big_label_font)
        self.do_change_button.setObjectName("do_change_button")
        self.do_change_button.setVisible(False)

        # 中间的分割线
        self.line = QtWidgets.QFrame(self.main_widget)
        self.line.setGeometry(QtCore.QRect(40, 90, 701, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        # 改签按钮
        self.change_time_button = QtWidgets.QPushButton(self.main_widget)
        self.change_time_button.setGeometry(QtCore.QRect(180, 270, 121, 31))
        self.change_time_button.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.change_time_button.setCheckable(False)
        self.change_time_button.setAutoDefault(False)
        self.change_time_button.setDefault(False)
        self.change_time_button.setFlat(False)
        self.change_time_button.setObjectName("change_time_button")

        # 预约座位按钮
        self.reserve_seat_button = QtWidgets.QPushButton(self.main_widget)
        self.reserve_seat_button.setGeometry(QtCore.QRect(390, 270, 121, 31))
        self.reserve_seat_button.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.reserve_seat_button.setCheckable(False)
        self.reserve_seat_button.setAutoDefault(False)
        self.reserve_seat_button.setDefault(False)
        self.reserve_seat_button.setFlat(False)
        self.reserve_seat_button.setObjectName("reserve_seat")

        # 修改个人信息按钮
        self.change_user_info_button = QtWidgets.QPushButton(self.main_widget)
        self.change_user_info_button.setGeometry(QtCore.QRect(570, 50, 121, 31))
        self.change_user_info_button.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.change_user_info_button.setCheckable(False)
        self.change_user_info_button.setAutoDefault(False)
        self.change_user_info_button.setDefault(False)
        self.change_user_info_button.setFlat(False)
        self.change_user_info_button.setObjectName("change_user_info_button")

        # 下侧输出框
        self.ui_console = QtWidgets.QTextBrowser(self.main_widget)
        self.ui_console.setGeometry(QtCore.QRect(35, 321, 721, 201))
        self.ui_console.setFont(console_font)
        self.ui_console.setObjectName("ui_console")

        # 场馆下拉文本框
        self.lib = QtWidgets.QComboBox(self.main_widget)
        self.lib.setGeometry(QtCore.QRect(120, 132, 141, 25))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.lib.sizePolicy().hasHeightForWidth())
        self.lib.setSizePolicy(size_policy)
        self.lib.setFont(normal_font)
        self.lib.setObjectName("lib")
        self.lib.addItems(utils.building_list)
        self.lib.setCurrentIndex(self.config["lib"])

        # 房间下拉文本框
        self.room = QtWidgets.QComboBox(self.main_widget)
        self.room.setGeometry(QtCore.QRect(120, 178, 141, 25))
        self.room.setSizePolicy(size_policy)
        self.room.setFont(normal_font)
        self.room.setObjectName("room")
        room_list = utils.room_index[self.config["lib"]]
        self.room.addItems(room_list)
        self.room.setCurrentIndex(self.config["room"])

        # 开始时间下拉文本框
        self.start_time = QtWidgets.QComboBox(self.main_widget)
        self.start_time.setGeometry(QtCore.QRect(410, 128, 141, 25))
        self.start_time.setSizePolicy(size_policy)
        self.start_time.setFont(normal_font)
        self.start_time.setObjectName("start_time")
        self.start_time.addItems(utils.start_time_list)
        self.start_time.setCurrentIndex(self.config["starttime"])

        # 结束时间下拉文本框
        self.end_time = QtWidgets.QComboBox(self.main_widget)
        self.end_time.setGeometry(QtCore.QRect(410, 174, 141, 25))
        self.end_time.setSizePolicy(size_policy)
        self.end_time.setFont(normal_font)
        self.end_time.setObjectName("end_time")
        self.end_time.addItems(utils.end_time_list[self.config["starttime"]:])
        self.rest_end_time = self.config["starttime"]  # 记录隐藏掉的end time列表，便于之后的保存
        self.end_time.setCurrentIndex(self.config["endtime"] - self.rest_end_time)

        # 靠窗下拉文本框
        self.window = QtWidgets.QComboBox(self.main_widget)
        self.window.setGeometry(QtCore.QRect(120, 222, 141, 25))
        self.window.setSizePolicy(size_policy)
        self.window.setFont(normal_font)
        self.window.setObjectName("window")
        self.window.addItems(utils.window_list)
        self.window.setCurrentIndex(self.config["window"])

        # 电源下拉文本框
        self.power = QtWidgets.QComboBox(self.main_widget)
        self.power.setGeometry(QtCore.QRect(410, 218, 141, 25))
        self.power.setSizePolicy(size_policy)
        self.power.setFont(normal_font)
        self.power.setObjectName("power")
        self.power.addItems(utils.power_list)
        self.power.setCurrentIndex(self.config["power"])

        # 场馆标签
        self.lib_label = QtWidgets.QLabel(self.main_widget)
        self.lib_label.setGeometry(QtCore.QRect(50, 134, 30, 20))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.lib_label.sizePolicy().hasHeightForWidth())
        self.lib_label.setSizePolicy(size_policy)
        self.lib_label.setFont(normal_font)
        self.lib_label.setTextFormat(QtCore.Qt.AutoText)
        self.lib_label.setObjectName("lib_label")

        # 靠窗标签
        self.window_label = QtWidgets.QLabel(self.main_widget)
        self.window_label.setGeometry(QtCore.QRect(50, 224, 60, 20))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.window_label.sizePolicy().hasHeightForWidth())
        self.window_label.setSizePolicy(size_policy)
        self.window_label.setFont(normal_font)
        self.window_label.setTextFormat(QtCore.Qt.AutoText)
        self.window_label.setObjectName("window_label")

        # 选择房间标签
        self.room_label = QtWidgets.QLabel(self.main_widget)
        self.room_label.setGeometry(QtCore.QRect(50, 180, 30, 20))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.room_label.sizePolicy().hasHeightForWidth())
        self.room_label.setSizePolicy(size_policy)
        self.room_label.setFont(normal_font)
        self.room_label.setTextFormat(QtCore.Qt.AutoText)
        self.room_label.setObjectName("room_label")

        # 开始时间标签
        self.start_time_label = QtWidgets.QLabel(self.main_widget)
        self.start_time_label.setGeometry(QtCore.QRect(320, 130, 60, 20))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.start_time_label.sizePolicy().hasHeightForWidth())
        self.start_time_label.setSizePolicy(size_policy)
        self.start_time_label.setFont(normal_font)
        self.start_time_label.setTextFormat(QtCore.Qt.AutoText)
        self.start_time_label.setObjectName("start_time_label")

        # 结束时间标签
        self.end_time_label = QtWidgets.QLabel(self.main_widget)
        self.end_time_label.setGeometry(QtCore.QRect(320, 176, 60, 20))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.end_time_label.sizePolicy().hasHeightForWidth())
        self.end_time_label.setSizePolicy(size_policy)
        self.end_time_label.setFont(normal_font)
        self.end_time_label.setTextFormat(QtCore.Qt.AutoText)
        self.end_time_label.setObjectName("end_time_label")

        # 电源标签
        self.power_label = QtWidgets.QLabel(self.main_widget)
        self.power_label.setGeometry(QtCore.QRect(320, 220, 75, 20))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.power_label.sizePolicy().hasHeightForWidth())
        self.power_label.setSizePolicy(size_policy)
        self.power_label.setFont(normal_font)
        self.power_label.setTextFormat(QtCore.Qt.AutoText)
        self.power_label.setObjectName("power_label")
        main_win.setCentralWidget(self.main_widget)

        self.retranslate_ui(main_win)

        # 下拉菜单部分按钮动作
        self.lib.currentIndexChanged.connect(self.get_room_list)
        self.start_time.currentIndexChanged.connect(self.get_end_time_list)

        # 修改个人信息部分按钮动作
        self.change_user_info_button.clicked.connect(self.change_user_info)
        self.do_change_button.clicked.connect(self.finish_change_user_info)

        # 改签、预约座位按钮动作
        self.change_time_button.clicked.connect(self.click_change_time_button)
        self.reserve_seat_button.clicked.connect(self.click_reserve_seat_button)

        # 重定向输出
        XStream.stdout().messageWritten.connect(self.ui_console.insertPlainText)
        XStream.stderr().messageWritten.connect(self.ui_console.insertPlainText)

        QtCore.QMetaObject.connectSlotsByName(main_win)

        main_win.setTabOrder(self.username_input, self.password_input)

    def retranslate_ui(self, main_win):
        _translate = QtCore.QCoreApplication.translate
        main_win.setWindowTitle(_translate("main_win", "武汉大学图书馆自习助手"))
        self.username_label.setText(_translate("main_win", "学 号 ：  {}".format(self.config["username"])))
        self.change_time_button.setText(_translate("main_win", "改签座位"))
        self.reserve_seat_button.setText(_translate("main_win", "预约座位"))
        self.change_user_info_button.setText(_translate("main_win", "修改个人信息"))
        self.lib_label.setText(_translate("main_win", "场馆"))
        self.window_label.setText(_translate("main_win", "是否靠窗"))
        self.room_label.setText(_translate("main_win", "房间"))
        self.start_time_label.setText(_translate("main_win", "开始时间"))
        self.end_time_label.setText(_translate("main_win", "结束时间"))
        self.power_label.setText(_translate("main_win", "是否有电源"))
        self.password_label.setText(_translate("main_win", "密 码 ："))
        self.do_change_button.setText(_translate("main_win", "确认"))

    def get_room_list(self):
        """
        更新房间下拉菜单
        :return: None
        """
        self.room.clear()
        self.room.addItems(utils.room_index[self.lib.currentIndex()])

    def get_end_time_list(self):
        """
        更新结束时间，让其显得符合逻辑
        :return: None
        """
        prev_rest_end_time = self.rest_end_time
        self.rest_end_time = start_time_current = self.start_time.currentIndex()
        end_time_current = self.end_time.currentIndex() + prev_rest_end_time
        self.end_time.clear()
        self.end_time.addItems(utils.end_time_list[self.start_time.currentIndex():])
        if start_time_current <= end_time_current:
            self.end_time.setCurrentIndex(end_time_current - self.rest_end_time)

    def change_user_info(self):
        """
        点击修改个人信息按钮的动作
        :return: None
        """
        self.username_label.setText("学 号 ：")
        self.username_input.setText("")
        self.password_input.setText("")

        self.username_input.setVisible(True)
        self.password_label.setVisible(True)
        self.password_input.setVisible(True)
        self.do_change_button.setVisible(True)
        self.change_user_info_button.setVisible(False)

        self.do_change_button.setShortcut(QtCore.Qt.Key_Enter)  # 按键盘上的回车即可快速提交

        self.username_input.setFocus()

    def finish_change_user_info(self):
        """
        点击确认按钮保存个人信息的按钮
        :return: None
        """
        self.username_input.setVisible(False)
        self.password_label.setVisible(False)
        self.password_input.setVisible(False)
        self.do_change_button.setVisible(False)
        self.change_user_info_button.setVisible(True)

        new_username = self.username_input.text() or ""
        new_password = self.password_input.text() or ""

        if new_username and new_username.isdigit():
            self.config["username"] = new_username
            if new_password:
                self.config["password"] = new_password

        self.username_label.setText("学 号 ： {}".format(self.config["username"]))

    def update_value(self):
        """
        获取下拉菜单的值
        :return: None
        """
        self.config["lib"] = self.lib.currentIndex()
        self.config["room"] = self.room.currentIndex()
        self.config["starttime"] = self.start_time.currentIndex()
        self.config["endtime"] = self.end_time.currentIndex() + self.rest_end_time
        self.config["window"] = self.window.currentIndex()
        self.config["power"] = self.power.currentIndex()

    def update_config_file(self):
        """
        保存config文件
        :return:
        """
        self.update_value()
        save_config(self.config.copy())

    def start_web_res(self):
        if self._web_res is None:
            self._web_res = webLogin.WebRes(self.config.copy())
        return self._web_res

    def start_app_res(self):
        if self._app_res is None:
            self._app_res = appLogin.AppRes(self.config.copy())
        return self._app_res

    def click_change_time_button(self):
        """
        点击改签座位的动作
        :return: None
        """
        if not self.change_time_thread:
            self.update_config_file()
            self.reserve_seat_button.setDisabled(True)
            self.change_time_button.setDisabled(True)
            self.change_time_thread = threading.Thread(
                target=self.change_time, name="change_time_thread", daemon=True
            )
            self.change_time_thread.start()
        else:
            self.change_time_thread = None
            self.change_time_button.setDisabled(False)
            self.reserve_seat_button.setDisabled(False)
            self.change_time_button.setText("改签座位")

    def click_reserve_seat_button(self):

        """
        点击预约座位的动作
        :return: None
        """
        if not self.reserve_seat_thread:
            self.update_config_file()
            self.reserve_seat_button.setText("停止操作")
            self.change_time_button.setDisabled(True)
            self.run_flag = True
            self.reserve_seat_thread = threading.Thread(
                target=self.reserve_seat, name="reserve_seat_thread", daemon=True
            )
            self.reserve_seat_thread.start()
        else:
            self.run_flag = False
            self.reserve_seat_thread = None
            self.change_time_button.setDisabled(False)
            self.reserve_seat_button.setText("预约座位")

    def change_time(self):
        """
        取消预约在预约的主函数
        :return: None
        """
        try:
            web_res = self.start_web_res()  # 登陆web端
            app_res = self.start_app_res()  # 登陆app端
            seat_id, res_id, seat_status = app_res.get_resevation_info()  # 获取预约信息
            if not seat_id:
                raise utils.ReserveStateError("当前没有预约")
            print("开始尝试重新预约...")
            if seat_status == "RESERVE":
                if not app_res.cancel_seat(res_id):  # 取消预约
                    raise utils.ReserveStateError("取消预约失败")
            else:
                assert app_res.stop_using()  # 释放座位
                if not app_res.cancel_seat(res_id):  # 取消预约
                    raise utils.ReserveStateError("取消预约失败")
            sleep(1)
            web_res.res_seat(seat_id)  # 尝试通过网页端重新预约
        finally:
            self.click_change_time_button()

    def reserve_seat(self):
        """
        搜索座位的主函数
        :return:
        """
        try:
            count = 1
            is_success = 0
            web_res = self.start_web_res()  # 登陆web端
            sleep(utils.get_rest_time())  # 判断是否进入等待模式
            while not is_success and self.run_flag:
                seat_list = web_res.free_search()
                while not seat_list:
                    print("【第{0}次搜索】目前没有空闲位置".format(count))
                    sleep(utils.interval_time + randint(0, 2))
                    seat_list = web_res.free_search()
                    count += 1

                print("【第{0}次搜索】发现空闲位置，尝试预约".format(count))
                sleep(1)
                seat = choice(seat_list)
                is_success = web_res.res_seat(seat)
                count += 1
        finally:
            if self.run_flag:
                self.click_reserve_seat_button()


class XStream(QtCore.QObject):
    """
    输出重定向
    """
    _stdout = None
    _stderr = None
    messageWritten = QtCore.pyqtSignal(str)

    def write(self, msg):
        """
        当调用write方法时，放出signal，添加进Text Browser控件
        :param msg:
        :return:
        """
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def flush():
        """
        emmmmm并不想重构，这个函数的作用是将当前缓冲区内所有的内容输出(print函数中有这一参数)
        :return:
        """
        pass

    @staticmethod
    def fileno():
        return -1

    @staticmethod
    def stdout():
        """
        模拟出标准输出类，从而实现重定向输出
        :return:
        """
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        """
        模拟出标准错误类，从而实现重定向输出
        :return:
        """
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


if __name__ == "__main__":
    whnd = windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        windll.user32.ShowWindow(whnd, 0)
        windll.kernel32.CloseHandle(whnd)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWin(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
