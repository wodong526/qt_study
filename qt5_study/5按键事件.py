import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)

        self.lab_a = QLabel('抬起')
        self.lab_a.setAlignment(Qt.AlignCenter)
        self.lab_b = QLabel('抬起')
        self.lab_b.setAlignment(Qt.AlignCenter)
        self.lab_c = QLabel('抬起')
        self.lab_c.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.lab_a)
        main_layout.addWidget(self.lab_b)
        main_layout.addWidget(self.lab_c)

    def keyPressEvent(self, event):
        #当有键盘按下时
        isAutoRepeat = event.isAutoRepeat()#按键长按时返回true

        if event.modifiers() == Qt.ShiftModifier:
            #按下的是修饰键，且为shift修饰键，在判断按下键时是否有辅助键时常用
            print('按下shift')
        if event.key() == Qt.Key_Shift:#按下的键为shift
            print('又shift')

        if isAutoRepeat:
            if event.key() == Qt.Key_Q:
                self.lab_a.setText('长按')
            elif event.key() == Qt.Key_W:
                self.lab_b.setText('长按')
            elif event.key() == Qt.Key_E:
                self.lab_c.setText('长按')
        else:
            if event.key() == Qt.Key_Q:
                self.lab_a.setText('按下')
            elif event.key() == Qt.Key_W:
                self.lab_b.setText('按下')
            elif event.key() == Qt.Key_E:
                self.lab_c.setText('按下')

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.lab_a.setText('抬起')
        elif event.key() == Qt.Key_W:
            self.lab_b.setText('抬起')
        elif event.key() == Qt.Key_E:
            self.lab_c.setText('抬起')




if __name__ == '__main__':#__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())