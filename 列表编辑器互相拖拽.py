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
        self.setAcceptDrops(True)#可以接受拖拽
        self.setDragEnabled(True)#可以进行拖拽

    def startDrag(self, supported_actions):
        #当项在拖拽时触发
        #此函数使用时可以注释以下已注释的两个函数，不复写该函数时可以取消下方已注释的函数，效果相同
        #使用该函数时需要打开当前控件的可被拖拽设置self.setDragEnabled(True)
        items = self.selectedItems()
        nodes = []
        for item in items:
            nodes.append(item.data(QtCore.Qt.UserRole))  # 获取到选中项的长名

        nodes_str = ' '.join(nodes)  # 用‘ ’拼接列表中的字符串
        mime_data = QtCore.QMimeData()
        mime_data.setData('aa/cc', QtCore.QByteArray(str(nodes_str)))  # 将与给定的MIME类型关联的数据设置为'aa'指定的nodes_str.

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)  # 将mime_data中的数据放到QDrag中
        drag.exec_()

    # def mousePressEvent(self, mouse_event):
    #     #鼠标按下时调用
    #     if mouse_event.button() == QtCore.Qt.LeftButton:
    #         self.drag_start_pos = mouse_event.pos()
    #
    #     super(DragAndDropNodeListWidget, self).mousePressEvent(mouse_event)

    # def mouseMoveEvent(self, mouse_event):
    #     #鼠标按下后移动时调用
    #     if mouse_event.buttons() & QtCore.Qt.LeftButton:#当按下的是鼠标按钮且是左键时
    #         if (mouse_event.pos() - self.drag_start_pos).manhattanLength() >= QtWidgets.QApplication.startDragDistance():
    #             #求差来判断光标移动距离是否满足为拖动操作
    #             items = self.selectedItems()
    #             nodes = []
    #             for item in items:
    #                 nodes.append(item.data(QtCore.Qt.UserRole))#获取到选中项的长名
    #
    #             nodes_str = ' '.join(nodes)#用‘ ’拼接列表中的字符串
    #             mime_data = QtCore.QMimeData()
    #             mime_data.setData('aa/cc', QtCore.QByteArray(str(nodes_str)))#将与给定的MIME类型关联的数据设置为'aa'指定的nodes_str.
    #
    #             drag = QtGui.QDrag(self)
    #             drag.setMimeData(mime_data)#将mime_data中的数据放到QDrag中
    #             drag.exec_()

    def dragEnterEvent(self, drag_event):
        #拖拽进入控件时
        if drag_event.mimeData().hasFormat('aa/cc'):
            drag_event.acceptProposedAction()

    def dragMoveEvent(self, drag_event):#鼠标在控件中移动
        #不复写为空就无法放下对象
        pass

    def dropEvent(self, drop_event):
        #当鼠标拖拽的对象被放到控件中时
        mime_data = drop_event.mimeData()
        if mime_data.hasFormat('aa/cc'):
            nodes_byte_array = mime_data.data('aa/cc')
            nodes_str = str(nodes_byte_array)
            nodes = nodes_str.split(' ')

            self.nodes_dropped.emit(nodes)


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

        self.refresh_listView()

    def create_widgets(self):
        self.lab_display_nam = QtWidgets.QLabel(u'显示的模型：')
        self.tree_display_view = DragAndDropNodeListWidget()

        self.lab_hide_nam = QtWidgets.QLabel(u'隐藏的模型：')
        self.tree_hide_view = DragAndDropNodeListWidget()

        self.but_right_move = QtWidgets.QPushButton('>>')
        self.but_right_move.setMaximumWidth(30)
        self.but_left_move = QtWidgets.QPushButton('<<')
        self.but_left_move.setMaximumWidth(30)

        self.but_refresh = QtWidgets.QPushButton(u'刷新')

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
            print '没有选择有效项。'

    def get_display(self):
        sel_items = self.tree_hide_view.selectedItems()
        if sel_items:
            long_obj = []
            for obj in sel_items:
                long_obj.append(obj.data(QtCore.Qt.UserRole))

            self.set_display(long_obj)
        else:
            print '没有选择有效项。'

    def set_hide(self, items):
        nodes = []
        for obj in items:
            try:
                mc.setAttr('{}.visibility'.format(obj), False)
            except:
                print '设置{}隐藏时出错，已跳过。'.format(obj)

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
                print '设置{}显示时出错，已跳过。'.format(obj)

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