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
        self.main_window.installEventFilter(self)#打开事件过滤器，所有在Maya窗口内的所有事件都会被传送

    def create_widgets(self):
        pass

    def create_layout(self):
        pass

    def create_connections(self):
        pass

    def print_hierarchy(self, widget):
        if widget:
            output = []
            name = widget.objectName()#获取焦点窗口名
            if not name:
                name = u'该聚焦对象没有名称'
            output.append(name)

            parent_widget = widget.parentWidget()#获取焦点窗口的父级
            while parent_widget:#当存在父级窗口时，就执行
                parent_name = parent_widget.objectName()#获取父级窗口名
                output.append(parent_name)
                parent_widget = parent_widget.parentWidget()#当父级窗口还有父级时，名称覆盖变量，当没有时，返回none，循环打断

            output.append('---')
            print '\n'.join(output)#用换行来连接这个列表

    def eventFilter(self, obj, event):
        if obj == self.main_window:
            if event.type() == QtCore.QEvent.Type.HoverMove:
                pos = QtGui.QCursor.pos()
                widget_under_mouse = QtWidgets.QApplication.widgetAt(pos)  # 通过鼠标所在位置来获取要查询的控件对象
                self.print_hierarchy(widget_under_mouse)

    def closeEvent(self, event):
        self.main_window.removeEventFilter(self)#在窗口关闭时关闭事件过滤器


if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()