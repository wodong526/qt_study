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
    def __init__(self, parent = maya_main_window()):
        super(TestWindow, self).__init__(parent)
        
        self.setWindowTitle(u'窗口抬头')
        if mc.about(ntOS = True):#判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)
        
        self.directory_path = 'C:/Users/Administrator/Documents/maya'
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        self.refresh_list()
    
    def create_widgets(self):
        self.show_in_folder_action = QtWidgets.QAction(u'在资源管理器中打开', self)
        
        self.path_label = QtWidgets.QLabel(self.directory_path)
        self.tree_wdg = QtWidgets.QTreeWidget()
        self.tree_wdg.setHeaderHidden(True)
        self.tree_wdg.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)#当被右击生成以什么形式的菜单，发出customContextMenuRequested()信号
        
        
        self.close_but = QtWidgets.QPushButton(u'取消')
    
    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_but)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.path_label)
        main_layout.addWidget(self.tree_wdg)
        main_layout.addLayout(button_layout)
    
    def create_connections(self):
        self.tree_wdg.customContextMenuRequested.connect(self.show_context_menu)
        
        self.show_in_folder_action.triggered.connect(self.show_in_folder)#信号为是否被点击
        self.close_but.clicked.connect(self.close)
    
    def refresh_list(self):
        self.tree_wdg.clear()
        
        self.add_chidren(None, self.directory_path)
    
    def add_chidren(self, parent_item, dir_path):
        directory = QtCore.QDir(dir_path)
        files_in_directory = directory.entryList(QtCore.QDir.NoDotAndDotDot ^ QtCore.QDir.AllEntries, QtCore.QDir.AllEntries ^ QtCore.QDir.IgnoreCase)
                                                #不显示目录开头的'.'和'..'，列出目录、文件、驱动器和符号链接，~，不区分大小写进行排序
        for file_name in files_in_directory:
            self.add_child(parent_item, dir_path, file_name)
    
    def add_child(self, parent_item, dir_path, file_name):
        file_path = '{}/{}'.format(dir_path, file_name)
        file_info = QtCore.QFileInfo(file_path)
        
        if file_info.suffix().lower() == 'pyc':
            return#当后缀是pyc时跳过当前项，为保险起见，进一步规定为小写
        
        item = QtWidgets.QTreeWidgetItem(parent_item, [file_name])
        item.setData(0, QtCore.Qt.UserRole, file_path)#为该项设置某信息，其它时候读取该项的data信息。可以为0号位通过序号为同一个项设置多个信息，获取信息时通过序号获取
        
        if file_info.isDir():#指定的fileInfo为目录时，回调函数，以当前info为父向下延申
            self.add_chidren(item, file_info.absoluteFilePath())
        
        if not parent_item:#当父级不存在时，直接在顶级创建项
            self.tree_wdg.addTopLevelItem(item)
    
    def show_context_menu(self, pos):
        #pos中的两个数对应在树型控件中的像素坐标
        item = self.tree_wdg.itemAt(pos)#通过坐标返回树状控件中的项
        if not item:#如果该位置没有项则不用生成上下文菜单
            return
        file_path = item.data(0, QtCore.Qt.UserRole)#返回该项的值，此处为路径
        self.show_in_folder_action.setData(file_path)#将内部数据设置为给定内容
        
        context_menu = QtWidgets.QMenu()#生成上下文菜单栏，但菜单栏里的项目可以用其它菜单来填充
        context_menu.addAction(self.show_in_folder_action)
        context_menu.exec_(self.tree_wdg.mapToGlobal(pos))
    
    def show_in_folder(self):
        file_path = self.show_in_folder_action.data()#返回给定的数据
        
        if mc.about(win = True):
            if self.open_in_explorer(file_path):
                return
        elif mc.about(mac = True):
            if self.open_in_finder(file_path):
                return
        
        '''使用这块代码无法做到打开文件所在目录时，选中该文件
        file_info = QtCore.QFileInfo(file_path)
        if file_info.isFile():#当为文件时，用资源管理器打开文件所在文件夹
            QtGui.QDesktopServices.openUrl(file_info.path())
        elif file_info.isDir():#当为文件夹时，用资源管理器打开该文件夹
            QtGui.QDesktopServices.openUrl(file_path)
        '''
    
    def open_in_explorer(self, file_path):
        file_info = QtCore.QFileInfo(file_path)
        args = []
        if file_info.isFile():
            args.append('/select,')
        args.append(QtCore.QDir.toNativeSeparators(file_path))#将路径信息转为windos适用的方式，如'/'改为'\'
        
        if QtCore.QProcess.startDetached('explorer', args):#运行字符串内写入的程序，后面列表里第一位为select则会选中该文件
            return True
        return False
    
    def open_in_finder(self, file_path):
        args = []
        args.append('-e')
        args.append('tell application "finder"')
        args.append('-e')
        args.append('activate')
        args.append('-e')
        args.append('select POSIX file "{0}"'.format(file_path))
        args.append('-e')
        args.append('end tell')
        args.append('-e')
        args.append('return')
        
        if (QtCore.QProcess.startDetached('/usr/bin/osascript', args)):
            return True

if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()