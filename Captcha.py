import tkinter as tk
from PIL import Image,ImageTk


class Id_Captcha:
    def __init__(self, img, string):
        self.pos = []
        self.app = tk.Tk()
        self.app.title("验证码")
        self.app.geometry("330x190+500+300")

        img = Image.open(img)
        self.img = ImageTk.PhotoImage(img)

        self.cap_label = tk.Label(self.app, image=self.img)
        self.cap_label.bind("<Button-1>", self.callback)
        self.cap_label.pack()

        self.str_label = tk.Label(self.app, text='请依次选择图中的"{}"，"{}"，"{}"'.format(*string[:3]))
        self.str_label.pack()

        self.app.mainloop()

    def callback(self, event):
        x = event.x
        y = event.y

        self.pos.append(
            {"x": x, "y": y}
        )

        # 长度到3时，就会自己关掉
        if len(self.pos) == 3:
            self.app.destroy()

    def get_pos(self):
        """
        获取位置坐标，便于主程序调用
        :return: dict
        """
        return self.pos
