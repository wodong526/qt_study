import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)

        self.move(0, 0)#移动到屏幕的某像素点，窗口、控件、屏幕的原点都在左上角
        self.setWindowIcon(QIcon('aaaaa.jpg'))#设置窗口图标，相对路径和绝对路径都行
        #self.setGeometry(0, 0, 800, 600)#等同于self.move + self.resize
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)#设置窗口旗标，当前为置顶
        self.setStyleSheet('background:rgb(100, 200, 200)')#设置窗口背景颜色（qt样式表）

        print(self.width())#获取窗口宽
        print(self.height())#获取窗口高
        print(self.size())#获取窗口宽和高
        print(self.pos())#获取窗口相对于父级的位置
        print(self.styleSheet())#窗口的样式表

        lab = QLabel()
        lab.setText('打标签')
        lab.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)#设置文本在上下左右都居中的位置
        #lab.setPixmap(QPixmap('aaaaa.jpg'))#给label设置图片

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(lab)

if __name__ == '__main__':#__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    #w.hide()#隐藏窗口
    #w.close()#关闭窗口
    sys.exit(app.exec_())