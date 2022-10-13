from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui
from functools import partial

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class CustomColorButton(QtWidgets.QLabel):
    def __init__(self, color = QtCore.Qt.white, parent = None):
        super(CustomColorButton, self).__init__(parent)
        self._color = QtGui.QColor()#无效颜色
        
        self.set_size(50, 14)
        self.set_color(color)
        
    def set_size(self, width, height):
        self.setFixedSize(width, height)
    
    def set_color(self, color):
        '''
        生成QtGui.QPixmap，并把它赋到label上
        '''
        color = QtGui.QColor(color)
        
        self._color = color
        
        pixmap = QtGui.QPixmap(self.size())
        pixmap.fill(self._color)
        self.setPixmap(pixmap)
    
    def get_color(self):
        return self._color
    
    def select_color(self):
        color = QtWidgets.QColorDialog.getColor(self.get_color(), self, u'选择控制器颜色', QtWidgets.QColorDialog.ShowAlphaChannel)
                                                #初始颜色，父窗口，标题，窗口模式，返回PySide2.QtGui.QColor
        if color.isValid():
            self.set_color(color)
    
    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.LeftButton:
            self.select_color()

class TestWindow(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()):
        super(TestWindow, self).__init__(parent)
        
        self.setWindowTitle(u'调色窗口')
        if mc.about(ntOS = True):#判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)
        
        self.setMinimumSize(300, 200)
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        self.foreground_color_but = CustomColorButton(QtCore.Qt.white)
        self.background_color_but = CustomColorButton(QtCore.Qt.black)
        
        
        self.print_but = QtWidgets.QPushButton(u'打印颜色rgb值')
        self.close_but = QtWidgets.QPushButton(u'取消')
    
    def create_layout(self):
        color_lyout = QtWidgets.QFormLayout(self)
        #不加self会导致maya设置父级时找不到qtlayout的objectName，加上不影响使用
        color_lyout.setObjectName('wharw')
        color_lyout.addRow(u'前景色', self.foreground_color_but)
        color_lyout.addRow(u'背景色', self.background_color_but)
        
        color_lyout.addRow(u'maya控件', self.add_cmdsWidget(color_lyout.objectName()))
        
        color_grp = QtWidgets.QGroupBox()
        color_grp.setLayout(color_lyout)
        
        ending_lyout = QtWidgets.QHBoxLayout()
        ending_lyout.addWidget(self.print_but)
        ending_lyout.addWidget(self.close_but)
        
        mainlyout = QtWidgets.QVBoxLayout(self)
        mainlyout.setContentsMargins(2, 2, 2, 2)
        mainlyout.addWidget(color_grp)
        mainlyout.addStretch()
        mainlyout.addLayout(ending_lyout)
    
    def create_connections(self):
        self.print_but.clicked.connect(self.print_colors)
        self.close_but.clicked.connect(self.close)
    
    def print_colors(self):
        fg_color = self.foreground_color_but.get_color()
        bg_color = self.background_color_but.get_color()
        
        print fg_color.red(), fg_color.green(), fg_color.blue()
        print bg_color.red(), bg_color.green(), bg_color.blue()
    
    def add_cmdsWidget(self, objName):
        mc.setParent(objName)
        self.sliderGrp = mc.colorSliderGrp(l = 'aa', rgb = (1, 0, 1), cc = self.print_color)
        ptr = omui.MQtUtil.findControl(self.sliderGrp)
        colLayout_Qt = wrapInstance(int(ptr), QtWidgets.QWidget)
        return colLayout_Qt
    
    def print_color(self, *args):
        print args
        print cmds.colorSliderGrp(self.sliderGrp, hsv = 1, q = 1)

if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()