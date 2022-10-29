# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
from shiboken2 import getCppPointer

import maya.cmds as mc
import maya.OpenMayaUI as omui

class WorkspaceControl(object):
    def __init__(self, nam):
        self.name = nam#窗口对象
        self.widget = None

    def create(self, label, widget, ui_script=None):
        '''
        创建窗口对象
        :param label:窗口抬头
        :param widget:qt窗口本身
        :param ui_script:附加到窗口的脚本
        :return:
        '''
        mc.workspaceControl(self.name, label=label)
        if ui_script:
            mc.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)

    def restore(self, widget):
        '''
        将qt控件放到maya窗口布局中
        :return:
        '''
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, wgt):
        '''
        将qt控件放到maya窗口布局中
        :param wgt: 要被放入的qt控件
        :return:
        '''
        if wgt:
            self.widget = wgt
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            workspace_control_ptr = int(omui.MQtUtil.findControl(self.name))
            widget_ptr = int(getCppPointer(self.widget)[0])
            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        '''
        检查这个窗口对象是否存在
        :return:
        '''
        return mc.workspaceControl(self.name, q=True, ex=True)

    def is_visible(self):
        '''
        检查窗口对象是否可见（关闭状态）
        :return:
        '''
        return mc.workspaceControl(self.name, q=True, vis=True)

    def set_visible(self, vis):
        '''
        使窗口控件展开或隐藏（关闭）
        :param vis:
        :return:
        '''
        if vis:
            mc.workspaceControl(self.name, e=True, rs=True)
        elif vis == False:
            mc.workspaceControl(self.name, e=True, vis=False)

    def set_lable(self, label):
        '''
        设置窗口对象的标题
        :param label:
        :return:
        '''
        mc.workspaceControl(self.name, e=True, l=label)

    def is_floating(self):
        '''
        检查窗口是否浮动
        :return:
        '''
        return mc.workspaceControl(self.name, q=True, fl=True)

    def is_collapsed(self):
        '''
        检查窗口是否折叠
        :return:
        '''
        return mc.workspaceControl(self.name, q=True, clp=True)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class TestWindow(QtWidgets.QWidget):

    UI_NAME = 'stopUi'
    ui_instance = None

    @classmethod
    def display(cls):
        if cls.ui_instance:
            cls.show_workspace_control()
        else:
            cls.ui_instance = TestWindow()

    @classmethod#在__init__之前运行后再给到这个类
    def get_workspace_control_name(cls):
        return '{}WorkspaceControl'.format(cls.UI_NAME)

    def __init__(self):
        super(TestWindow, self).__init__()

        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.window_tite = u'怎么回事'

        self.setObjectName(self.__class__.UI_NAME)
        self.setMinimumSize(200, 100)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_workspace_control()

    def create_widgets(self):
        self.but = QtWidgets.QPushButton(u'哈哈')

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.but)

    def create_connections(self):
        self.but.clicked.connect(self.print_tex)

    def print_tex(self):
        print 11

    def create_workspace_control(self):
        '''
        将该窗口设置为可停靠
        :return:
        '''
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control_instance.exists():#如果存在则显示，不存在就生成
            self.workspace_control_instance.restore(self)
        else:
            self.workspace_control_instance.create(self.window_tite, self, 'from test_win import TestWindow\nTestWindow.display()')

    def show_workspace_control(self):
        '''
        显示停靠窗口
        :return:
        '''
        self.workspace_control_instance.set_visible(True)

    def showEvent(self, e):
        '''
        在不同窗口环境下使用不同的窗口标题
        :param e:
        :return:
        '''
        if self.workspace_control_instance.is_floating():
            self.workspace_control_instance.set_lable(u'浮动窗口')
        else:
            self.workspace_control_instance.set_lable(u'停靠窗口')

if __name__ == '__main__':
    my_workspace_name = TestWindow.get_workspace_control_name()
    if mc.window(my_workspace_name, ex=True):
        mc.deleteUI(my_workspace_name)

    try:
        sample_ui.setParent(None)
        sample_ui.deleteLater()
    except:
        pass
    finally:
        sample_ui = TestWindow()
        sample_ui.show()