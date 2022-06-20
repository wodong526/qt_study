import pstats
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class WindowClassName(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()) -> None:
        super(SpinBoxDialog, self).__init__(parent)

        self.setWindowTitle('窗口抬头')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self) -> None:
        pass
    
    def create_layout(self) -> None:
        pass
    
    def create_connections(self) -> None:
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