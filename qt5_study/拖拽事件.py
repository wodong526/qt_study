import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class myLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(myLineEdit, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):#拖拽进入事件
        super().dragEnterEvent(event)#将原来该事件的功能保留
        text = event.mimeData().text()
        print(text)

    def dropEvent(self, event):
        text = event.mimeData().text()#获取拖拽的信息
        self.setText(text)

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)

        lin_a = myLineEdit()
        lin_b = myLineEdit()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(lin_a)
        main_layout.addWidget(lin_b)

if __name__ == '__main__':#__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())