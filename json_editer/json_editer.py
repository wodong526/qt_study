import datetime
import os
import json
import sys
from PySide2 import QtCore, QtGui, QtWidgets

class JsonEditer(QtWidgets.QWidget):
    FILE_PATH = r'F:\Chris Zurbrigg Tutorials\Python in Production\11-python_in_production-a_practical_json_example_part_1'
    JSON_PATH = 'assets.json'

    IMAGE_WIDTH = 400
    IMAGE_HEIGHT = IMAGE_WIDTH / 1.77778

    def __init__(self):
        super(JsonEditer, self).__init__(parent = None)

        self.setWindowTitle('测试')
        self.setMinimumSize(400, 300)

        self.json_path = '{}/{}'.format(self.FILE_PATH, self.JSON_PATH)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.set_edit_enabled(False)

        self.load_ass_from_json()

    def create_widgets(self):
        self.ass_label = QtWidgets.QLabel('asset code')
        self.ass_cmb = QtWidgets.QComboBox()

        self.preview_image_label = QtWidgets.QLabel()
        self.preview_image_label.setFixedHeight(self.IMAGE_HEIGHT)#属于qtwiget方法，设置控件的最小和最大高度值都为某值，但不更改宽度

        self.name_le = QtWidgets.QLineEdit()
        self.description_plaintext = QtWidgets.QPlainTextEdit()   #纯文本编辑器，与文本编辑器textEdit不同
        self.description_plaintext.setFixedHeight(100)
        self.creator_le = QtWidgets.QLineEdit()
        self.created_data_le = QtWidgets.QLineEdit()
        self.modified_date_le = QtWidgets.QLineEdit()

        self.edit_button = QtWidgets.QPushButton('编辑')
        self.save_button = QtWidgets.QPushButton('保存')
        self.canecl_button = QtWidgets.QPushButton('取消')
    
    def create_layout(self):
        ass_list_layout = QtWidgets.QHBoxLayout()
        ass_list_layout.addStretch()             #使控件不可被拉伸
        ass_list_layout.addWidget(self.ass_label)
        ass_list_layout.addWidget(self.ass_cmb)

        details_layout = QtWidgets.QFormLayout()
        details_layout.addRow('名字:', self.name_le)
        details_layout.addRow('描述:', self.description_plaintext)
        details_layout.addRow('作者:', self.creator_le)
        details_layout.addRow('创建时间:', self.created_data_le)
        details_layout.addRow('改动时间:', self.modified_date_le)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.canecl_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)#使该布局的上下左右与其它布局与控件之间的距离为多少，默认为11个像素
        main_layout.addLayout(ass_list_layout)
        main_layout.addWidget(self.preview_image_label)
        main_layout.addLayout(details_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.ass_cmb.currentTextChanged.connect(self.refresh_ass_details)#返回下拉框的当前文本currentIndexChanged为返回当前栏的编号

        self.edit_button.clicked.connect(self.edit_ass_details)
        self.save_button.clicked.connect(self.save_ass_details)
        self.canecl_button.clicked.connect(self.cancel_edit)
    
    def set_edit_enabled(self, enabled):
        read_only = not enabled

        self.name_le.setReadOnly(read_only)
        self.description_plaintext.setReadOnly(read_only)#setReadOnly意为使该控件是否可被编辑，当为1时不可被编辑
        if read_only:#创建时间和修改时间不可手动编辑
            self.creator_le.setReadOnly(read_only)
            self.created_data_le.setReadOnly(read_only)
            self.modified_date_le.setReadOnly(read_only)
        
        self.edit_button.setVisible(read_only) #是否隐藏,为0时可见
        self.save_button.setHidden(read_only)  #是否可见,为1时可见
        self.canecl_button.setHidden(read_only)#同属于qwiget类
    
    def set_preview_image(self, file_name):
        image_path = '{}/{}'.format(self.FILE_PATH, file_name)#图片路径

        file_info = QtCore.QFileInfo(image_path)#转为qtcore类型的路径
        if file_info.exists():#当该路径存在时
            image = QtGui.QImage(image_path)#将图片信息转为qtgui.qimage类型的信息
            #生成一个给定高度和宽度的矩形框副本、使用尽可能保持原图像比例的方法放置图像、使用平滑方式转换图像
            image = image.scaled(self.preview_image_label.width(), self.preview_image_label.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            pixmap = QtGui.QPixmap()
            pixmap.convertFromImage(image)#将qpixmap对象替换为给定的图像
        
        else:
            pixmap = QtGui.QPixmap(self.preview_image_label.size())
            pixmap.fill(QtCore.Qt.magenta)#如果没有找到图片，则使用一个色彩对象覆盖该label（可选颜色）
        
        self.preview_image_label.setPixmap(pixmap)#设置图片到label控件
    
    def load_ass_from_json(self):
        with open(self.json_path, 'r') as file_read:
            self.ass = json.load(file_read)
        
        for ass_code in self.ass.keys():
            self.ass_cmb.addItem(ass_code)#为组合框添加项目
    
    def save_ass_to_json(self):
        with open(self.json_path, 'w') as w:
            json.dump(self.ass, w, indent = 4)
    
    def refresh_ass_details(self, cmb_str):
        current_ass = self.ass[cmb_str]

        self.name_le.setText(current_ass['name'])
        self.description_plaintext.setPlainText(current_ass['description'])
        self.creator_le.setText(current_ass['creator'])
        self.created_data_le.setText(current_ass['created'])
        self.modified_date_le.setText(current_ass['modified'])

        QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))#不加入这一行会导致读不到图片对象
        self.set_preview_image(current_ass['image_path'])
    
    def edit_ass_details(self):
        self.set_edit_enabled(True)
    
    def save_ass_details(self):#点击保存时
        self.set_edit_enabled(False)#保存和取消按钮不可见，且行编辑器不可设置

        modified = datetime.datetime.now()#获取当前时间
        self.modified_date_le.setText(modified.strftime('%Y/%m/%d %H:%M:%S'))#将时间格式化

        ass_code = self.ass_cmb.currentText()#获取当前组合框的键

        current_ass = self.ass[ass_code]#获取当前键的所有键值!!这里是浅拷贝，虽然是从ass字典中拷贝出，但还是指向同一个内存，即修改任意变量的值都会对对方的值造成影响
        #使所有键值依次对应到修改后的文本
        current_ass['name'] = self.name_le.text()
        current_ass['description'] = self.description_plaintext.toPlainText()
        current_ass['modified'] = self.modified_date_le.text()

        self.save_ass_to_json()
    
    def cancel_edit(self):#如果点击取消
        self.set_edit_enabled(False)#保存和取消按钮不可见，且行编辑器不可设置
        self.refresh_ass_details(self.ass_cmb.currentText())#对行编辑器填入json文本里对应的内容

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('fusion'))#将控件设置为更好看的圆角

    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(143, 117, 150))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(208, 208, 208))

    app.setPalette(dark_palette)

    a = JsonEditer()
    a.show()

    app.exec_()
