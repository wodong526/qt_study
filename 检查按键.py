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
        ���̰���ʱ����
        '''
        ctrl = key_event.modifiers() == QtCore.Qt.ControlModifier
        print ctrl
        shift = key_event.modifiers() == QtCore.Qt.ShiftModifier
        print shift
        alt = key_event.modifiers() == QtCore.Qt.AltModifier
        print alt

        #��������ͬʱ����ʱ�������ж�����Ϊ�٣���Ҫ������ķ����ж��Ƿ���ͬʱ���µļ�
        ctrl_alt = key_event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier)
        print ctrl_alt

        key = key_event.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if ctrl:
                print ('ִ�д���')
                return
            elif ctrl_alt:
                print ('����')
                return

        '''if key == QtCore.Qt.Key_A:
            print '����A'
        elif key == QtCore.Qt.Key_Return:
            print 'return'
        elif key == QtCore.Qt.Key_Enter:
            print 'enter' '''

        super(MyPlainTextEdit, self).keyPressEvent(key_event)#���Ϻ���������������ʾ����ַ���������ʾ
        print u'��ӡ{}'.format(key_event.text())

    def keyReleaseEvent(self, key_event):
        '''
        ���̻ص�ʱ����
        '''
        super(MyPlainTextEdit, self).keyReleaseEvent(key_event)
        print 'ʲô'


class TestWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TestWindow, self).__init__(parent)

        self.setWindowTitle(u'����̧ͷ')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
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