from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class WindowClassName(QtWidgets.QWidget):#使该窗口为控件
    def __init__(self, parent = maya_main_window()):
        super(WindowClassName, self).__init__(parent)

        self.setWindowTitle('窗口抬头')
        if mc.about(ntOS = True):#判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)#指定该小部件为显示窗口，拥有最大化和最小化按钮，设置为Dialog会变回原样
                                                        #当13行换回Dialog时，指定该flags仍然会保留最大最小按钮，详情看文档
        self.setWindowTitle('ssjs')
        self.setMinimumSize(300, 200)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        pass
    
    def create_layout(self):
        pass
    
    def create_connections(self):
        pass

if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = WindowClassName()
        my_window.show()