# WHULibSeatReservation
武汉大学图书馆座位预约脚本，同时实现了自习助手APP端和网页端的模拟登陆。支持定时抢座、持续扫描抢座、座位改签，操作简单

## 版本要求
本程序要求Python 3版本

使用了PyQt5和requests，需要自行安装，方法见下

## 界面展示

<div align=center>
  <img src="https://github.com/idocx/WHULibSeatReservation/blob/master/demo.jpg" height="500"/>
</div>


## 使用方法
### >Windows平台
Windows推荐下载的Python 3版本：[下载连接](https://www.anaconda.com/distribution/)

运行```Setup.exe```文件，系统将自动安装PyQt5和requests（需要安装了Python和pip，若按上面链接安装则已经自动安装了pip）

国内pip的使用可能需要换源，Windows下pip换源方法：[教程](https://blog.csdn.net/Artprog/article/details/75632723)

完成安装以后运行```武汉大学图书馆自习助手.exe```即可正常启动。

### >MacOS平台
目前只能通过源码进行使用

先装一下Python，[安装教程](https://pythonguidecn.readthedocs.io/zh/latest/starting/install3/osx.html)

打开终端（启动台->Terminal），安装一下相关库，命令```pip install PyQt5 requests```

然后打开终端，切换到程序所在目录，输入```python3 main_win.py```即可（也可以写一个```.command```文件简化操作）

### >Linux平台
```pass```
