from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class SpinBoxDialog(QtWidgets.QDialog):
    def __init__(self, parent = maya_main_window()) -> None:
        super(SpinBoxDialog, self).__init__(parent)

        self.setWindowTitle('整型与浮点测试')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)#删除窗口上的帮助按钮

        self.create_widgets()
        self.create_layout()
        self.create_connections()
    
    def create_widgets(self) -> None:
        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setFixedWidth(80)
        self.spin_box.setMinimum(30)#最小值
        self.spin_box.setMaximum(90)#最大值
        self.spin_box.setSingleStep(50)#步长
        self.spin_box.setPrefix('@')#加前缀
        self.spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)#去掉末尾的上下键

        self.doubleSpin_box = QtWidgets.QDoubleSpinBox()
        self.doubleSpin_box.setFixedWidth(80)
        self.doubleSpin_box.setSuffix('m')#加后缀
    
    def create_layout(self) -> None:
        main_layout = QtWidgets.QFormLayout(self)
        main_layout.addRow('整型', self.spin_box)
        main_layout.addRow('双精度整型', self.doubleSpin_box)
    
    def create_connections(self) -> None:
        self.spin_box.valueChanged.connect(self.print_value)
        self.doubleSpin_box.valueChanged.connect(self.print_value)
    
    def print_value(self, value) -> None:
        print('alue:{}'.format(value))

if __name__ == '__main__':
    try:
        spin_box_dialog.close()
        spin_box_dialog.deleteLater()
    except:
        pass
    finally:
        spin_box_dialog = SpinBoxDialog()
        spin_box_dialog.show()