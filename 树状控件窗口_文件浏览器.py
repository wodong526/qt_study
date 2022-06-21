from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as mc

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class TreeViewDialog(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()):
        super(TreeViewDialog, self).__init__(parent)

        self.setWindowTitle(u'树状布局')

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮

        self.setMinimumSize(700, 400)

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self):
        root_path = '{}/2020/scripts'.format(mc.internalVar(uad = 1))#获取文档目录
        
        self.mode = QtWidgets.QFileSystemModel()
        self.mode.setRootPath(root_path)
#        self.mode.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)#依次为列出过滤器的文件目录，不要列出"."和"..",列出文件（不写也是这个效果）
        self.mode.setNameFilters(["*.py"])#只能选中列出的后缀的文件，其余文件为灰色不能点击，文件夹能点击
        self.mode.setNameFilterDisables(False)#将非此后缀的文件隐藏，包括文件夹
        
        self.tree_view = QtWidgets.QTreeView()
        self.tree_view.setModel(self.mode)
        self.tree_view.setRootIndex(self.mode.index(root_path))
#        self.tree_view.hideColumn(1)#隐藏序列为1的列
        self.tree_view.setColumnWidth(0, 240)#设置序列为1的行宽
    
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)#属于QLayout方法，设置该layout的上下左右边距
        main_layout.addWidget(self.tree_view)
    
    def create_connections(self):
        self.tree_view.doubleClicked.connect(self.on_double_print)
    
    def on_double_print(self, inf):
        path = self.mode.filePath(inf)
        if self.mode.isDir(inf):
            print 'yes {}'.format(path)
        else:
            print 'no {}'.format(path)

if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TreeViewDialog()
        my_window.show()