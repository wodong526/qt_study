from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class CustomImageWidget(QtWidgets.QWidget):
    def __init__(self, width, heigth, image_path, parent = None):
        super(CustomImageWidget, self).__init__(parent)
        
        self.set_size(width, heigth)
        self.set_image(image_path)
        self.set_background_color(QtCore.Qt.red)
    
    def set_size(self, width, height):
        self.setFixedSize(width, height)
    
    def set_image(self, image_path):
        image = QtGui.QImage(image_path)
        image = image.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
        
        self.pixmap = QtGui.QPixmap()
        self.pixmap.convertFromImage(image)
        self.update()
    
    def set_background_color(self, color):
        self.background_color = color
        self.update()#刷新小部件
    
    def paintEvent(self, event):#该方法在小部件上进行绘制事件event
        painter = QtGui.QPainter(self)#实例化绘图操作
        
        painter.fillRect(0, 0, self.width(), self.height(), self.background_color)#拥有多种绘制方式，从0，0所在像素开始，绘制一个w，h这么大的矩形，颜色为color
        painter.drawPixmap(self.rect(), self.pixmap)#保持小部件内部几何图形、图片

class testWindow(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()):
        super(testWindow, self).__init__(parent)

        self.setWindowTitle(u'窗口抬头')
        if mc.about(ntOS = True):#判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        image_path = "F:/cc.png"
        '''
        image = QtGui.QImage(image_path)#实例化
        image = image.scaled(300, 100, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)#缩放，缩放尺寸，大小自由变化，不保留纵横比，
                                                                                                            #将图形平滑，否则缩放后会有锯齿
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        
        
        self.lab = QtWidgets.QLabel('ssssss')
        self.lab.setPixmap(pixmap)
        '''
        self.labl = CustomImageWidget(300, 300, image_path)
        self.switch_but = QtWidgets.QPushButton(u'切换')
        
    
    def create_layout(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addWidget(self.labl)
        mainLayout.addWidget(self.switch_but)
    
    def create_connections(self):
        self.switch_but.clicked.connect(self.set_background_green)
    
    def set_background_green(self):
        self.labl.set_background_color(QtCore.Qt.green)
    
if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = testWindow()
        my_window.show()