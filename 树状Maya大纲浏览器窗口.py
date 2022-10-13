from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

from functools import partial

import maya.OpenMayaUI as omui
import maya.cmds as mc

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class TreeViewDialog(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()):
        super(TreeViewDialog, self).__init__(parent)

        self.setWindowTitle(u'树状布局')
        if mc.about(nt = 1):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(mac = 1):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(700, 400)
        
        self.script_job_number = -1
        
        self.create_actions()
        self.crate_icon()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
        self.refresh_tree_widget()

    def create_actions(self):
        self.about_action = QtWidgets.QAction(QtGui.QIcon(':help.png'), u'关于')
        
        self.display_action = QtWidgets.QAction(u'形状')
        self.display_action.setCheckable(True)#生成复选框
        self.display_action.setChecked(True)#勾选复选框
        self.display_action.setShortcut(QtGui.QKeySequence('Ctrl+Shift+H'))

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()#生成菜单栏
        display_menu = self.menu_bar.addMenu(u'显示')
        display_menu.addAction(self.display_action)
        help_menu = self.menu_bar.addMenu(u'帮助')
        help_menu.addAction(self.about_action)
        
        self.refresh_but = QtWidgets.QPushButton(u'刷新')
        
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)#使可以按ctrl或shift来多选
        self.tree_widget.setHeaderHidden(True)#隐藏分类栏
        header = self.tree_widget.headerItem()
        header.setText(0, u'拉拉')#给分类栏添加分类
    
    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
#        button_layout.addStretch()#将控件变为默认大小并按参数比例放置位置
        button_layout.addWidget(self.refresh_but)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)#属于QLayout方法，设置该layout的上下左右边距
        main_layout.setSpacing(2)#在该布局内每个控件之间的距离，默认为10
        main_layout.addWidget(self.menu_bar)
        main_layout.addWidget(self.tree_widget)
        main_layout.addLayout(button_layout)
    
    def create_connections(self):
        self.refresh_but.clicked.connect(self.refresh_tree_widget)
        self.tree_widget.itemCollapsed.connect(self.update_icon)#项目关闭
        self.tree_widget.itemExpanded.connect(self.update_icon)#项目展开
        self.tree_widget.itemSelectionChanged.connect(self.select_items)
     
    def refresh_tree_widget(self):
        self.tree_widget.clear()
        top_dagNode = mc.ls(assemblies = 1)
        for n in top_dagNode:
            item = self.create_item(n)
            self.tree_widget.addTopLevelItem(item)
        
        self.update_selection()
    
    def create_item(self, name):
        item = QtWidgets.QTreeWidgetItem([name])
        self.add_children(item)
        self.update_icon(item)
        
        return item
    
    def add_children(self, inf):
        children = mc.listRelatives(inf.text(0), children = 1)
        if children:
            for child in children:
                child_inf = self.create_item(child)
                inf.addChild(child_inf)
    
    def update_icon(self, item):
        object_type = ''

        if item.isExpanded():#项目是否展开，返回布尔
            object_type = mc.nodeType(item.text(0))
        else:
            child_count = item.childCount()
            if child_count == 0:
                object_type = mc.nodeType(item.text(0))
            elif child_count == 1:
                child_item = item.child(0)
                object_type = mc.nodeType(child_item.text(0))
            else:
                object_type = 'transform'
        
        if object_type == 'transform':
            item.setIcon(0, self.transform_ico)
        elif object_type == 'camera':
            item.setIcon(0, self.camera_icon)
        elif object_type == 'mesh':
            item.setIcon(0, self.mesh_icon)
    
    def select_items(self):
        item_lis = self.tree_widget.selectedItems()
        obj_n = []
        for item in item_lis:
            obj_n.append(item.text(0))
        
        mc.select(obj_n, r = 1)
    
    def crate_icon(self):
        self.transform_ico = QtGui.QIcon(':transform.svg')
        self.camera_icon = QtGui.QIcon(':Camera.png')
        self.mesh_icon = QtGui.QIcon(':mesh.svg')
    
    def show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.display_action)
        context_menu.addSeparator()#分割线
        context_menu.addAction(self.about_action)
        
        context_menu.exec_(self.mapToGlobal(point))
    
    def update_selection(self):
        selection = mc.ls(sl = 1)
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            is_selected = item.text(0) in selection
            item.setSelected(is_selected)
            
            iterator += 1
    
    def set_script_job_enabed(self, enabled):
        if enabled and self.script_job_number < 0:
            self.script_job_number = mc.scriptJob(event = ['SelectionChanged', partial(self.update_selection)], protected = 1)#当字符串效果产生，就执行后面的作业代码（在该作业代码没有被关闭前会持续运行）
        elif not enabled and self.script_job_number >= 0:
            mc.scriptJob(kill = self.script_job_number, force = 1)#关闭受保护的作业
            self.script_job_number = -1
    
    def showEvent(self, e):
        super(TreeViewDialog, self).showEvent(e)
        self.set_script_job_enabed(True)
    
    def closeEvent(self, e):
        if isinstance(self, TreeViewDialog):
            super(TreeViewDialog, self).closeEvent(e)
            self.set_script_job_enabed(False)

if __name__ == '__main__':
    try:
        simple_outliner.set_script_job_enabed(False)
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TreeViewDialog()
        my_window.show()