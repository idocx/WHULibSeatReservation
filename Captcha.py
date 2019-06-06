from tkinter import *
from PIL import Image,ImageTk


class Id_Captcha:
    def __init__(self, img, string):
        self.pos = []
        self.app = Tk()
        self.app.title("验证码")

        img = Image.open(img)
        self.img = ImageTk.PhotoImage(img)

        self.cap_label = Label(self.app, image=self.img)
        self.cap_label.bind("<Button-1>", self.callback)
        self.cap_label.pack()

        self.str_label = Label(self.app, text='请依次选择图中的"{}"，"{}"，"{}"'.format(*string[:3]))
        self.str_label.pack()

        self.app.mainloop()

    def callback(self, event):
        x = event.x
        y = event.y

        self.pos.append(
            {"x": x, "y": y}
        )
        if len(self.pos) == 3:
            self.app.destroy()

    def get_pos(self):
        return self.pos


