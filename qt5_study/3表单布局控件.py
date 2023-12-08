import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class myLab(QLabel):
    mouseRelease = pyqtSignal(str)

    def __init__(self, image_path, tex):
        super(myLab, self).__init__()
        self.setFixedSize(100, 120)
        self.text = tex

        lab_image = QLabel()
        lab_image.setPixmap(QPixmap(image_path))
        lab_image.setAlignment(Qt.AlignCenter)#使左右居中

        lab_text = QLabel()
        lab_text.setText(tex)
        lab_text.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPixelSize(20)#高度为20像素
        lab_text.setFont(font)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(lab_image)
        main_layout.addWidget(lab_text)

    def mouseReleaseEvent(self, event):
        if event.button == Qt.RightButton:
            self.mouseRelease.emit(self.text)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)

        dir_lis = listdir('F:/qt5_open/')
        img_lis = []
        for file in dir_lis:
            if file.split('.')[-1] == 'png':
                img_lis.append(file)

        self.lis_wid = QListWidget()
        self.lis_wid.setFlow(QListWidget.LeftToRight)#将item布局改为从左到右
        self.lis_wid.setWrapping(True)#启动允许换行
        self.lis_wid.setResizeMode(QListWidget.Adjust)#允许窗口缩放时自动换行
        self.lis_wid.setSelectionMode(QAbstractItemView.ExtendedSelection)#使可以同时选中多个项
        self.lis_wid.itemDoubleClicked.connect(self.printng)#使用单击信号时会崩溃
        for i in range(len(img_lis)):
            lab = myLab(img_lis[i], str(i))
            #lab.mouseRelease.connect(self.printng)
            item = QListWidgetItem()
            item.setData(Qt.UserRole, img_lis[i])#给item附加信息
            item.setSizeHint(lab.size())

            self.lis_wid.addItem(item)
            self.lis_wid.setItemWidget(item, lab)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.lis_wid)

    def printng(self):
        items = self.lis_wid.selectedItems()
        for item in items:
            print(item.data(Qt.UserRole))#读取item上的附加信息


if __name__ == '__main__':#__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())