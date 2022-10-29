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
        self.name = nam#���ڶ���
        self.widget = None

    def create(self, label, widget, ui_script=None):
        '''
        �������ڶ���
        :param label:����̧ͷ
        :param widget:qt���ڱ���
        :param ui_script:���ӵ����ڵĽű�
        :return:
        '''
        mc.workspaceControl(self.name, label=label)
        if ui_script:
            mc.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)

    def restore(self, widget):
        '''
        ��qt�ؼ��ŵ�maya���ڲ�����
        :return:
        '''
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, wgt):
        '''
        ��qt�ؼ��ŵ�maya���ڲ�����
        :param wgt: Ҫ�������qt�ؼ�
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
        ���������ڶ����Ƿ����
        :return:
        '''
        return mc.workspaceControl(self.name, q=True, ex=True)

    def is_visible(self):
        '''
        ��鴰�ڶ����Ƿ�ɼ����ر�״̬��
        :return:
        '''
        return mc.workspaceControl(self.name, q=True, vis=True)

    def set_visible(self, vis):
        '''
        ʹ���ڿؼ�չ�������أ��رգ�
        :param vis:
        :return:
        '''
        if vis:
            mc.workspaceControl(self.name, e=True, rs=True)
        elif vis == False:
            mc.workspaceControl(self.name, e=True, vis=False)

    def set_lable(self, label):
        '''
        ���ô��ڶ���ı���
        :param label:
        :return:
        '''
        mc.workspaceControl(self.name, e=True, l=label)

    def is_floating(self):
        '''
        ��鴰���Ƿ񸡶�
        :return:
        '''
        return mc.workspaceControl(self.name, q=True, fl=True)

    def is_collapsed(self):
        '''
        ��鴰���Ƿ��۵�
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

    @classmethod#��__init__֮ǰ���к��ٸ��������
    def get_workspace_control_name(cls):
        return '{}WorkspaceControl'.format(cls.UI_NAME)

    def __init__(self):
        super(TestWindow, self).__init__()

        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.window_tite = u'��ô����'

        self.setObjectName(self.__class__.UI_NAME)
        self.setMinimumSize(200, 100)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_workspace_control()

    def create_widgets(self):
        self.but = QtWidgets.QPushButton(u'����')

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.but)

    def create_connections(self):
        self.but.clicked.connect(self.print_tex)

    def print_tex(self):
        print 11

    def create_workspace_control(self):
        '''
        ���ô�������Ϊ��ͣ��
        :return:
        '''
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control_instance.exists():#�����������ʾ�������ھ�����
            self.workspace_control_instance.restore(self)
        else:
            self.workspace_control_instance.create(self.window_tite, self, 'from test_win import TestWindow\nTestWindow.display()')

    def show_workspace_control(self):
        '''
        ��ʾͣ������
        :return:
        '''
        self.workspace_control_instance.set_visible(True)

    def showEvent(self, e):
        '''
        �ڲ�ͬ���ڻ�����ʹ�ò�ͬ�Ĵ��ڱ���
        :param e:
        :return:
        '''
        if self.workspace_control_instance.is_floating():
            self.workspace_control_instance.set_lable(u'��������')
        else:
            self.workspace_control_instance.set_lable(u'ͣ������')

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