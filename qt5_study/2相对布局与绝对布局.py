import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class myBut(QPushButton):
    printText = pyqtSignal(str)

    def __init__(self):
        super(myBut, self).__init__()

    def mousePressEvent(self, event):
        self.printText.emit('信号')


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)

        '''
        but_a = QPushButton('a', parent=self)
        but_a.move(0, 0)

        but_b = QPushButton('b', parent=self)
        but_b.move(200, 100)'''
        #这是绝对布局，控件不会随窗口缩放而改变缩放与位置，且声明控件时要指定父级

        but_a = QPushButton('a')
        but_b = QPushButton('b')
        but_c = QPushButton('c')

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(but_a)
        main_layout.addWidget(but_b)
        main_layout.addWidget(but_c)
        #这是相对布局
        

if __name__ == '__main__':#__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())