# WHULibSeatReservation
武汉大学图书馆座位预约脚本，同时实现了自习助手APP端和网页端的模拟登陆。支持定时抢座、持续扫描抢座、座位改签，操作简单

## 版本要求
本程序要求Python 3版本

使用了pillow这个第三方库，需要自行安装，方法见下

## 使用方法
### >Windows平台
直接下载文件，阅读使用说明即可使用

[文件下载地址](https://www.chemhy.design/wp-content/uploads/WHULibRes.rar)


### >MacOS平台
目前只能通过源码进行使用

先装一下Python，[安装教程](https://pythonguidecn.readthedocs.io/zh/latest/starting/install3/osx.html)

打开终端（启动台->Terminal），安装一下pillow库，命令```pip install pillow```

然后打开终端，切换到程序所在目录，输入```python3 UI.py```即可（也可以写一个```.command```文件简化操作）

### >Linux平台
用Linux的还要教程？建议不会用的自己写一个（微笑
