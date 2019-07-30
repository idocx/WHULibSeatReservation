#############################################################
#                        作者：我.doc                        #
# Github地址：https://github.com/idocx/WHULibSeatReservation #
#############################################################

import tkinter as tk


class SetUserinfo(tk.Toplevel):
    def __init__(self, root):
        super(SetUserinfo, self).__init__(master=root)
        self.root = root

        self.title("修改个人信息")
        self.geometry("310x180+500+300")

        # 获取焦点
        self.focus()

        # 学号输入框
        self.username_text = tk.Label(self, text="学号")
        self.username_text.grid(row=0, column=0, ipady=20, ipadx=30)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, ipady=0, ipadx=0)

        # 密码输入框
        self.password_text = tk.Label(self, text="密码")
        self.password_text.grid(row=1, column=0, ipady=20, ipadx=30)
        self.password_entry = tk.Entry(self)
        self.password_entry["show"] = "●"
        self.password_entry.grid(row=1, column=1, ipady=0, ipadx=0)

        self.change_button = tk.Button(self, text="确认", command=self.record_change)
        self.change_button.grid(row=3, column=1, ipady=2, ipadx=20)

    def record_change(self):
        """
        记录相应的值
        :return:
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username:
            self.root.username = username
        if password:
            self.root.password = password

        self.root.var_name.set("学号：{}".format(username))
        self.destroy()


if __name__ == "__main__":
    pass
