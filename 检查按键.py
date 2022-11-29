# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class MyPlainTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super(MyPlainTextEdit, self).__init__(parent)

    def keyPressEvent(self, key_event):
        '''
        键盘按下时触发
        '''
        ctrl = key_event.modifiers() == QtCore.Qt.ControlModifier
        print ctrl
        shift = key_event.modifiers() == QtCore.Qt.ShiftModifier
        print shift
        alt = key_event.modifiers() == QtCore.Qt.AltModifier
        print alt

        #当两个键同时按下时，以上判定都会为假，需要用下面的方法判断是否有同时按下的键
        ctrl_alt = key_event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier)
        print ctrl_alt

        key = key_event.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if ctrl:
                print ('执行代码')
                return
            elif ctrl_alt:
                print ('换行')
                return

        '''if key == QtCore.Qt.Key_A:
            print '按下A'
        elif key == QtCore.Qt.Key_Return:
            print 'return'
        elif key == QtCore.Qt.Key_Enter:
            print 'enter' '''

        super(MyPlainTextEdit, self).keyPressEvent(key_event)#加上后可以在输入框内显示打的字符，否则不显示
        print u'打印{}'.format(key_event.text())

    def keyReleaseEvent(self, key_event):
        '''
        键盘回弹时触发
        '''
        super(MyPlainTextEdit, self).keyReleaseEvent(key_event)
        print '什么'


class TestWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TestWindow, self).__init__(parent)

        self.setWindowTitle(u'窗口抬头')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.pltex = MyPlainTextEdit()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.pltex)

    def create_connections(self):
        pass


if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()