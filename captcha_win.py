# -*- coding: utf-8 -*-

# captcha_win implementation generated from reading ui file 'captcha.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import utils
import logo_rc


class CaptchaWin(QtWidgets.QDialog):
    def __init__(self, cap_text, cap_pic, parent=None):
        super(CaptchaWin, self).__init__(parent)
        self.pos = []

        self.setObjectName("captcha_win")
        self.setFixedSize(330, 195)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        normal_font = QtGui.QFont()
        normal_font.setFamily(utils.font_name)
        normal_font.setPointSize(utils.font_size+2)

        # 设置图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/LOGO/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setAutoFillBackground(False)

        # 验证码文字标签
        self.captcha_text = QtWidgets.QLabel(self)
        self.captcha_text.setGeometry(QtCore.QRect(0, 165, 330, 30))
        self.captcha_text.setFont(normal_font)
        self.captcha_text.setAlignment(QtCore.Qt.AlignHCenter)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.captcha_text.sizePolicy().hasHeightForWidth())
        self.captcha_text.setSizePolicy(size_policy)
        self.captcha_text.setObjectName("captcha_text")

        # 验证码图片部分
        self.captcha_pic = QtWidgets.QLabel(self)
        self.captcha_pic.setGeometry(QtCore.QRect(0, 0, 330, 160))
        pix_map = QtGui.QPixmap()
        pix_map.loadFromData(cap_pic, "jpg")
        self.captcha_pic.setPixmap(pix_map)
        self.captcha_pic.setScaledContents(True)
        self.captcha_pic.setObjectName("captcha_pic")

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("captcha_win", "验证码"))
        self.captcha_text.setText(_translate(
            "captcha_win", "请依次选择图中的\"{}\"，\"{}\"，\"{}\"").format(*cap_text[:3])
        )

        QtCore.QMetaObject.connectSlotsByName(self)

    def mousePressEvent(self, event):
        """
        点击鼠标时，记录鼠标位置
        :param event: 点击鼠标事件
        :return: None
        """
        x, y = event.pos().x(), event.pos().y()
        self.pos.append(
            {"x": x, "y": y}
        )
        # 长度到3时，就会自己关掉
        if len(self.pos) >= 3:
            self.close()

    def get_pos(self):
        """
        获取位置坐标，供程序调用
        :return: dict
        """
        return self.pos


if __name__ == '__main__':
    pass
