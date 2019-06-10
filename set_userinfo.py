import tkinter as tk
import utils


class SetUserinfo:
    def __init__(self, root):
        self.root = root

        # 建立Toplevel
        self.userinfo_win = tk.Toplevel()
        self.userinfo_win.title("修改个人信息")
        self.userinfo_win.geometry("350x240+500+300")

        # 获取焦点
        self.userinfo_win.focus()

        # 学号输入框
        self.username_text = tk.Label(self.userinfo_win, text="学号")
        self.username_text.grid(row=0, column=0, ipady=20, ipadx=50)
        self.username_entry = tk.Entry(self.userinfo_win)
        self.username_entry.grid(row=0, column=1, ipady=0, ipadx=0)

        # 密码输入框
        self.password_text = tk.Label(self.userinfo_win, text="密码")
        self.password_text.grid(row=1, column=0, ipady=20, ipadx=50)
        self.password_entry = tk.Entry(self.userinfo_win)
        self.password_entry["show"] = "●"
        self.password_entry.grid(row=1, column=1, ipady=0, ipadx=0)

        # 姓名输入框
        self.name_text = tk.Label(self.userinfo_win, text="姓名")
        self.name_text.grid(row=2, column=0, ipady=20, ipadx=50)
        self.name_entry = tk.Entry(self.userinfo_win)
        self.name_entry.grid(row=2, column=1, ipady=0, ipadx=0)

        self.change_button = tk.Button(self.userinfo_win, text="确认", command=self.record_change)
        self.change_button.grid(row=3, column=1, ipady=2, ipadx=20)

    def record_change(self):
        """
        记录相应的值
        :return:
        """
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if name:
            self.root.name = name
        if username:
            self.root.username = username
        if password:
            self.root.password = password

        self.root.var_name.set("学号：{}                    姓名：{}".format(username, name))
        self.userinfo_win.destroy()


if __name__ == "__main__":
    pass
