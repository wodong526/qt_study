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

        self.main_window = maya_main_window()
        self.main_window.installEventFilter(self)
        #伪代码，self为main_window所在窗体，main_window上触发的事件会发送给窗体进行处理（检测事件）

    def create_widgets(self):
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.installEventFilter(self)
        self.comb_box = QtWidgets.QComboBox()
        self.comb_box.addItems([u'高', u'中', u'低'])

    def create_layout(self):
        main_layout = QtWidgets.QFormLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)

        main_layout.addRow(u'名字', self.line_edit)
        main_layout.addRow(u'啊', self.comb_box)

    def create_connections(self):
        pass

    def eventFilter(self, obj, event):
        #事件检测都会传到这里
        if obj == self.main_window:
            #当监测对象是Maya主窗口
            if event.type() == QtCore.QEvent.Close:
                #当监测到的类型是关闭窗口
                result = QtWidgets.QMessageBox.question(self, u'确定关闭', u'确定关闭？')
                if result == QtWidgets.QMessageBox.No:
                    event.ignore()
                    return True
        elif obj == self.line_edit:
            #当检测的是这个控件
            if event.type() == QtCore.QEvent.KeyPress:#当类型为按键
                if event.key() == QtCore.Qt.Key_A:#当按键为A时
                    print 1
            elif event.type() == QtCore.QEvent.FocusIn:#当类型为聚焦到时
                print 2
            elif event.type() == QtCore.QEvent.FocusOut:#当类型为取消聚焦时
                print 3

        return False



if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()