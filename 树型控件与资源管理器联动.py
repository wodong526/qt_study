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
        
        self.setWindowTitle(u'����̧ͷ')
        if mc.about(ntOS = True):#�ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#ɾ�������ϵİ�����ť
        elif mc.about(macOS = True):
            self.setWindowFlags(QtCore.Qt.Tool)
        
        self.directory_path = 'C:/Users/Administrator/Documents/maya'
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        self.refresh_list()
    
    def create_widgets(self):
        self.show_in_folder_action = QtWidgets.QAction(u'����Դ�������д�', self)
        
        self.path_label = QtWidgets.QLabel(self.directory_path)
        self.tree_wdg = QtWidgets.QTreeWidget()
        self.tree_wdg.setHeaderHidden(True)
        self.tree_wdg.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)#�����һ�������ʲô��ʽ�Ĳ˵�������customContextMenuRequested()�ź�
        
        
        self.close_but = QtWidgets.QPushButton(u'ȡ��')
    
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
        
        self.show_in_folder_action.triggered.connect(self.show_in_folder)#�ź�Ϊ�Ƿ񱻵��
        self.close_but.clicked.connect(self.close)
    
    def refresh_list(self):
        self.tree_wdg.clear()
        
        self.add_chidren(None, self.directory_path)
    
    def add_chidren(self, parent_item, dir_path):
        directory = QtCore.QDir(dir_path)
        files_in_directory = directory.entryList(QtCore.QDir.NoDotAndDotDot ^ QtCore.QDir.AllEntries, QtCore.QDir.AllEntries ^ QtCore.QDir.IgnoreCase)
                                                #����ʾĿ¼��ͷ��'.'��'..'���г�Ŀ¼���ļ����������ͷ������ӣ�~�������ִ�Сд��������
        for file_name in files_in_directory:
            self.add_child(parent_item, dir_path, file_name)
    
    def add_child(self, parent_item, dir_path, file_name):
        file_path = '{}/{}'.format(dir_path, file_name)
        file_info = QtCore.QFileInfo(file_path)
        
        if file_info.suffix().lower() == 'pyc':
            return#����׺��pycʱ������ǰ�Ϊ�����������һ���涨ΪСд
        
        item = QtWidgets.QTreeWidgetItem(parent_item, [file_name])
        item.setData(0, QtCore.Qt.UserRole, file_path)#Ϊ��������ĳ��Ϣ������ʱ���ȡ�����data��Ϣ������Ϊ0��λͨ�����Ϊͬһ�������ö����Ϣ����ȡ��Ϣʱͨ����Ż�ȡ
        
        if file_info.isDir():#ָ����fileInfoΪĿ¼ʱ���ص��������Ե�ǰinfoΪ����������
            self.add_chidren(item, file_info.absoluteFilePath())
        
        if not parent_item:#������������ʱ��ֱ���ڶ���������
            self.tree_wdg.addTopLevelItem(item)
    
    def show_context_menu(self, pos):
        #pos�е���������Ӧ�����Ϳؼ��е���������
        item = self.tree_wdg.itemAt(pos)#ͨ�����귵����״�ؼ��е���
        if not item:#�����λ��û�����������������Ĳ˵�
            return
        file_path = item.data(0, QtCore.Qt.UserRole)#���ظ����ֵ���˴�Ϊ·��
        self.show_in_folder_action.setData(file_path)#���ڲ���������Ϊ��������
        
        context_menu = QtWidgets.QMenu()#���������Ĳ˵��������˵��������Ŀ�����������˵������
        context_menu.addAction(self.show_in_folder_action)
        context_menu.exec_(self.tree_wdg.mapToGlobal(pos))
    
    def show_in_folder(self):
        file_path = self.show_in_folder_action.data()#���ظ���������
        
        if mc.about(win = True):
            if self.open_in_explorer(file_path):
                return
        elif mc.about(mac = True):
            if self.open_in_finder(file_path):
                return
        
        '''ʹ���������޷��������ļ�����Ŀ¼ʱ��ѡ�и��ļ�
        file_info = QtCore.QFileInfo(file_path)
        if file_info.isFile():#��Ϊ�ļ�ʱ������Դ���������ļ������ļ���
            QtGui.QDesktopServices.openUrl(file_info.path())
        elif file_info.isDir():#��Ϊ�ļ���ʱ������Դ�������򿪸��ļ���
            QtGui.QDesktopServices.openUrl(file_path)
        '''
    
    def open_in_explorer(self, file_path):
        file_info = QtCore.QFileInfo(file_path)
        args = []
        if file_info.isFile():
            args.append('/select,')
        args.append(QtCore.QDir.toNativeSeparators(file_path))#��·����ϢתΪwindos���õķ�ʽ����'/'��Ϊ'\'
        
        if QtCore.QProcess.startDetached('explorer', args):#�����ַ�����д��ĳ��򣬺����б����һλΪselect���ѡ�и��ļ�
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