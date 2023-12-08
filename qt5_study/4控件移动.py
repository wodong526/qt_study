import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class myLab(QLabel):
    def __init__(self):
        super(myLab, self).__init__()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #self.old_pos = event.pos()
            self.old_pos = QCursor.pos()#加上self反而无法正常运行

    # def mouseMoveEvent(self, event):
    #     enw_pos = event.pos()
    #     if (enw_pos - self.old_pos).manhattanLength() >= QApplication.startDragDistance():
    #         self.move(self.mapToParent(enw_pos - self.old_pos))
    #将注释替换，也可以做到移动控件

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_pos = QCursor.pos()
            delta_pos = new_pos - self.old_pos
            self.move(self.pos() + delta_pos)
            self.old_pos = new_pos


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)

        self.lab = myLab()
        self.lab.setParent(self)
        self.lab.setFixedSize(50, 50)
        self.lab.setStyleSheet('background:rgb(100, 0, 0)')
        self.lab.move(100, 200)


if __name__ == '__main__':#__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())