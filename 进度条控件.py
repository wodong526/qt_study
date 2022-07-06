import time
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

def maya_main_window():
    maya_main_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(maya_main_ptr), QtWidgets.QWidget)

class ProgressTestDialg(QtWidgets.QDialog):
    WINDOW_TITLE = 'progress_test'

    def __init__(self, parent = maya_main_window()):
        super(ProgressTestDialg, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
#        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#去除标题栏上的问号
        self.setWindowFlags(QtCore.Qt.WindowType.Window)#在标题栏上生成最大化最小化按钮
        
        self.setMinimumSize(400, 400)
        self.test_in_progress = False
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        self.progress_bar_button = QtWidgets.QPushButton(u'加载')
        self.progress_bar = QtWidgets.QProgressBar()#进度条控件
        self.progress_bar.setRange(0, 10)#设置进度条范围
        
        
        self.progress_bar_label = QtWidgets.QLabel(u'等待加载')
        self.cancel_button = QtWidgets.QPushButton(u'取消')
        
        self.dup_vis()
    
    def create_layout(self):
        progres_layout = QtWidgets.QVBoxLayout()
        progres_layout.addWidget(self.progress_bar_label)
        progres_layout.addWidget(self.progress_bar)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.progress_bar_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addLayout(progres_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        
    def create_connections(self):
        self.progress_bar_button.clicked.connect(self.run_progress_test)
        self.cancel_button.clicked.connect(self.cancel_progress_test)

    def dup_vis(self):
        self.progress_bar_label.setVisible(self.test_in_progress)
        self.progress_bar.setVisible(self.test_in_progress)
        self.progress_bar_button.setHidden(self.test_in_progress)
        self.cancel_button.setVisible(self.test_in_progress)
    
    def run_progress_test(self):
        if self.test_in_progress:
            return False
        self.progress_bar.setValue(0)
        self.progress_bar_label.setText(u'正在加载·····')
        self.test_in_progress = True
        self.dup_vis()
        
        for i in range(11):
            if not self.test_in_progress:
                break
            
            self.progress_bar_label.setText(u'已加载{}0%'.format(i))
            self.progress_bar.setValue(i)
            time.sleep(0.5)#使进程暂停0.5秒
            
            QtCore.QCoreApplication.processEvents()#释放进程 使可以操作其它控件
        
        self.test_in_progress = False
        self.dup_vis()
        self.progress_bar.reset()#将进度条回归
        self.progress_bar_label.setText(u'等待加载')
    
    def cancel_progress_test(self):
        self.test_in_progress = False
    
    
''' 单独生成进度条
    def run_progress_test(self):
        number_of_operations = 10
        
        progress_dialog = QtWidgets.QProgressDialog(u'正在加载······', u'取消', 0, number_of_operations, self)
        progress_dialog.setWindowTitle(u'计时器')
        progress_dialog.setWindowFlags(progress_dialog.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        progress_dialog.setValue(0)
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        progress_dialog.show()
        QtCore.QCoreApplication.processEvents()
        
        for i in range(1, number_of_operations + 1):
            if progress_dialog.wasCanceled():
                break
                
            progress_dialog.setLabelText(u'已完成{}/{}'.format(i, number_of_operations))
            progress_dialog.setValue(i)
            time.sleep(1)
            
            QtCore.QCoreApplication.processEvents()'''
            
        
if __name__ == '__main__':
    try:
        test_dialog.close()
        test_dialog.deleteLater()
    except:
        pass
    finally:
        test_dialog = ProgressTestDialg()
        test_dialog.show()