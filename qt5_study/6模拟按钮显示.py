import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class myButton(QWidget):
    def __init__(self, text='按钮', parent=None):
        super(myButton, self).__init__(parent)
        self._state = 0  # 指示此时鼠标不在控件上、悬停在控件上、按下控件
        self._background_color = None  # 控件颜色
        self._frame_color = None  # 控件边框颜色
        self.tex = text

        self.setAttribute(Qt.WA_StyledBackground)  # QWidget默认是透明的，用这个使控件不透明
        self.setMaximumHeight(40)

    def enterEvent(self, event):  # 鼠标进入控件时
        # super(myButton, self).enterEvent(event)
        self._state = 1
        self.update()

    def leaveEvent(self, event):  # 鼠标移出控件时
        # super(myButton, self).leaveEvent(event)
        self._state = 0
        self.update()

    def mousePressEvent(self, event):  # 鼠标按下控件时
        # super(myButton, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._state = 2
        self.update()

    def mouseReleaseEvent(self, event):  # 鼠标弹起时
        # super(myButton, self).mouseReleaseEvent(event)
        if self.rect().contains(event.pos()):  # 当鼠标位置在控件内
            self._state = 1
        else:
            self._state = 0
        self.update()

    def paintEvent(self, event):  # 绘制事件
        if self._state == 0:
            self._background_color = QColor(225, 225, 225)
            self._frame_color = QColor(173, 173, 173)
        elif self._state == 1:
            self._background_color = QColor(229, 241, 251)
            self._frame_color = QColor(0, 120, 215)
        elif self._state == 2:
            self._background_color = QColor(205, 228, 246)
            self._frame_color = QColor(3, 87, 156)

        p = QPainter()
        p.begin(self)

        p.setPen(Qt.NoPen)  # 不绘制实际线段
        p.setBrush(QBrush(self._frame_color))
        p.drawRect(self.rect())  # self.rect()是控件的范围

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._background_color))
        p.drawRect(self.rect().adjusted(1, 1, -1, -1))  # 在控件范围上的上下左右都内推一个像素

        p.setPen(Qt.black)
        font = QFont()
        font.setFamily('微软雅黑')
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignCenter, self.tex)

        p.end()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)

        but = myButton()
        but_a = QPushButton()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(but)
        main_layout.addWidget(but_a)


if __name__ == '__main__':  # __name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    # sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
