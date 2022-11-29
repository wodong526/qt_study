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

class DragAndDropNodeListWidget(QtWidgets.QListWidget):
    nodes_dropped = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(DragAndDropNodeListWidget, self).__init__(parent)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)#���Խ�����ק
        self.setDragEnabled(True)#���Խ�����ק

    def startDrag(self, supported_actions):
        #��������קʱ����
        #�˺���ʹ��ʱ����ע��������ע�͵���������������д�ú���ʱ����ȡ���·���ע�͵ĺ�����Ч����ͬ
        #ʹ�øú���ʱ��Ҫ�򿪵�ǰ�ؼ��Ŀɱ���ק����self.setDragEnabled(True)
        items = self.selectedItems()
        nodes = []
        for item in items:
            nodes.append(item.data(QtCore.Qt.UserRole))  # ��ȡ��ѡ����ĳ���

        nodes_str = ' '.join(nodes)  # �á� ��ƴ���б��е��ַ���
        mime_data = QtCore.QMimeData()
        mime_data.setData('aa/cc', QtCore.QByteArray(str(nodes_str)))  # ���������MIME���͹�������������Ϊ'aa'ָ����nodes_str.

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)  # ��mime_data�е����ݷŵ�QDrag��
        drag.exec_()

    # def mousePressEvent(self, mouse_event):
    #     #��갴��ʱ����
    #     if mouse_event.button() == QtCore.Qt.LeftButton:
    #         self.drag_start_pos = mouse_event.pos()
    #
    #     super(DragAndDropNodeListWidget, self).mousePressEvent(mouse_event)

    # def mouseMoveEvent(self, mouse_event):
    #     #��갴�º��ƶ�ʱ����
    #     if mouse_event.buttons() & QtCore.Qt.LeftButton:#�����µ�����갴ť�������ʱ
    #         if (mouse_event.pos() - self.drag_start_pos).manhattanLength() >= QtWidgets.QApplication.startDragDistance():
    #             #������жϹ���ƶ������Ƿ�����Ϊ�϶�����
    #             items = self.selectedItems()
    #             nodes = []
    #             for item in items:
    #                 nodes.append(item.data(QtCore.Qt.UserRole))#��ȡ��ѡ����ĳ���
    #
    #             nodes_str = ' '.join(nodes)#�á� ��ƴ���б��е��ַ���
    #             mime_data = QtCore.QMimeData()
    #             mime_data.setData('aa/cc', QtCore.QByteArray(str(nodes_str)))#���������MIME���͹�������������Ϊ'aa'ָ����nodes_str.
    #
    #             drag = QtGui.QDrag(self)
    #             drag.setMimeData(mime_data)#��mime_data�е����ݷŵ�QDrag��
    #             drag.exec_()

    def dragEnterEvent(self, drag_event):
        #��ק����ؼ�ʱ
        if drag_event.mimeData().hasFormat('aa/cc'):
            drag_event.acceptProposedAction()

    def dragMoveEvent(self, drag_event):#����ڿؼ����ƶ�
        #����дΪ�վ��޷����¶���
        pass

    def dropEvent(self, drop_event):
        #�������ק�Ķ��󱻷ŵ��ؼ���ʱ
        mime_data = drop_event.mimeData()
        if mime_data.hasFormat('aa/cc'):
            nodes_byte_array = mime_data.data('aa/cc')
            nodes_str = str(nodes_byte_array)
            nodes = nodes_str.split(' ')

            self.nodes_dropped.emit(nodes)


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

        self.refresh_listView()

    def create_widgets(self):
        self.lab_display_nam = QtWidgets.QLabel(u'��ʾ��ģ�ͣ�')
        self.tree_display_view = DragAndDropNodeListWidget()

        self.lab_hide_nam = QtWidgets.QLabel(u'���ص�ģ�ͣ�')
        self.tree_hide_view = DragAndDropNodeListWidget()

        self.but_right_move = QtWidgets.QPushButton('>>')
        self.but_right_move.setMaximumWidth(30)
        self.but_left_move = QtWidgets.QPushButton('<<')
        self.but_left_move.setMaximumWidth(30)

        self.but_refresh = QtWidgets.QPushButton(u'ˢ��')

    def create_layout(self):
        display_layout = QtWidgets.QVBoxLayout()
        display_layout.addWidget(self.lab_display_nam)
        display_layout.addWidget(self.tree_display_view)

        hide_layout = QtWidgets.QVBoxLayout()
        hide_layout.addWidget(self.lab_hide_nam)
        hide_layout.addWidget(self.tree_hide_view)

        move_layout = QtWidgets.QVBoxLayout()
        move_layout.addWidget(self.but_right_move)
        move_layout.addWidget(self.but_left_move)

        function_layout = QtWidgets.QHBoxLayout()
        function_layout.addLayout(display_layout)
        function_layout.addLayout(move_layout)
        function_layout.addLayout(hide_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(function_layout)
        main_layout.addWidget(self.but_refresh)

    def create_connections(self):
        self.but_right_move.clicked.connect(self.get_hide)
        self.but_left_move.clicked.connect(self.get_display)

        self.tree_display_view.nodes_dropped.connect(self.set_display)
        self.tree_hide_view.nodes_dropped.connect(self.set_hide)

        self.but_refresh.clicked.connect(self.refresh_listView)

    def refresh_listView(self):
        self.tree_display_view.clear()
        self.tree_hide_view.clear()

        mesh_lis = mc.ls(typ='mesh')
        for mesh in mesh_lis:
            trs = mc.listRelatives(mesh, p=True)[0]
            trs_long = mc.listRelatives(mesh, p=True, f=True)[0]

            item = QtWidgets.QListWidgetItem(trs)
            item.setData(QtCore.Qt.UserRole, trs_long)

            if mc.getAttr('{}.visibility'.format(trs_long)) == True:
                self.tree_display_view.addItem(item)
            else:
                self.tree_hide_view.addItem(item)

    def get_hide(self):
        sel_items = self.tree_display_view.selectedItems()
        if sel_items:
            long_obj = []
            for obj in sel_items:
                long_obj.append(obj.data(QtCore.Qt.UserRole))

            self.set_hide(long_obj)
        else:
            print 'û��ѡ����Ч�'

    def get_display(self):
        sel_items = self.tree_hide_view.selectedItems()
        if sel_items:
            long_obj = []
            for obj in sel_items:
                long_obj.append(obj.data(QtCore.Qt.UserRole))

            self.set_display(long_obj)
        else:
            print 'û��ѡ����Ч�'

    def set_hide(self, items):
        nodes = []
        for obj in items:
            try:
                mc.setAttr('{}.visibility'.format(obj), False)
            except:
                print '����{}����ʱ������������'.format(obj)

        self.refresh_listView()
        for i in range(self.tree_hide_view.count()):
            item = self.tree_hide_view.item(i)
            if item.data(QtCore.Qt.UserRole) in nodes:
                self.tree_display_view.setCurrentRow(i, QtCore.QItemSelectionModel.Select)

    def set_display(self, items):
        nodes = []
        for obj in items:
            try:
                mc.setAttr('{}.visibility'.format(obj), True)
            except:
                print '����{}��ʾʱ������������'.format(obj)

        self.refresh_listView()
        for i in range(self.tree_display_view.count()):
            item = self.tree_display_view.item(i)
            if item.data(QtCore.Qt.UserRole) in nodes:
                self.tree_hide_view.setCurrentRow(i, QtCore.QItemSelectionModel.Select)

if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()