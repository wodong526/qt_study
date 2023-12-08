import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Board(QWidget):
    def __init__(self, parent=None):
        super(Board, self).__init__(parent)
        self.setFixedSize(600, 600)
        self.setMouseTracking(True)  # 跟踪鼠标
        self.setCursor(Qt.BlankCursor)#设置鼠标外观为空白
        self.setAcceptDrops(True)  #可以接受拖拽

        self._brush_color = QColor(255, 0, 0)  # 画笔初始颜色
        self._brush_size = 10  # 画笔直径
        self._is_drawing = False  # 画笔是否处于绘制状态
        self._tool = 'brush'

        self._last_pressed_mouse_pos = None
        self._current_pressed_mouse_pos = None

        self._canvas = QPixmap(self.size())
        self._canvas.fill(Qt.transparent)  # 画布是透明的，同QColor (0, 0, 0, 0)

    def grid_pixmap(self):
        pix = QPixmap(2, 2)  # 生成一个长宽为2像素的map
        pix.fill(QColor(200, 200, 200))  # 设置底色为灰色

        p = QPainter()
        p.begin(pix)
        # 生成背景
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 255, 255)))  # 填充白色像素
        p.drawRect(QRect(0, 0, 1, 1))  # 从0,0到1,1像素的像素块填充
        p.drawRect(QRect(1, 1, 2, 2))  # 从0,0到2,2像素的像素块填充

        p.end()
        return pix

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing, True)#抗锯齿

        p.setPen(Qt.NoPen)
        brush = QBrush()
        brush.setTexture(self.grid_pixmap().scaled(20, 20))  # 给笔刷设置图片和缩放
        p.setBrush(brush)
        p.drawRect(self.rect())  # 绘制范围

        p.drawPixmap(self.rect(), self._canvas)  # 在当前控件范围内绘制该画布

        p.setPen(QPen(Qt.black, 1))
        p.setBrush(Qt.NoBrush)
        center = self.mapFromGlobal(QCursor.pos())  # 获取鼠标在屏幕空间的位置
        p.drawEllipse(QRect(center - QPoint(int(self._brush_size / 2), int(self._brush_size / 2)),
                            center + QPoint(int(self._brush_size / 2), int(self._brush_size / 2))))#绘图器的绘制椭圆方法

        p.end()

    def mousePressEvent(self, event):  # 按下
        if event.button() == Qt.LeftButton:
            self._is_drawing = True
            self._last_pressed_mouse_pos = QCursor.pos()
            self._current_pressed_mouse_pos = QCursor.pos()

    def mouseMoveEvent(self, event):  # 按下并移动
        if self._is_drawing:
            self._current_pressed_mouse_pos = QCursor.pos()  # 结束位置为鼠标被移动到的位置
            p = QPainter()
            p.begin(self._canvas)

            # pen = QPen()
            # pen.setStyle(Qt.SolidLine)  # 绘画模式：持续的线
            # pen.setWidth(self._brush_size)  # 画笔半径
            # pen.setColor(self._brush_color)  # 画笔颜色
            # pen.setStyle(Qt.RoundCap)#画笔为圆头
            # pen.setJoinStyle(Qt.RoundJoin)#画笔转折圆滑过渡
            p.setPen(Qt.NoPen)
            # brush = QBrush()
            # brush.setColor(self._brush_color)#用这两行会导致画不出颜色
            p.setBrush(QBrush(self._brush_color))
            p.setRenderHint(QPainter.Antialiasing, True)#绘制的图形加抗锯齿

            if self._tool == 'reaser':  # 当画笔为橡皮擦时
                p.setCompositionMode(QPainter.CompositionMode_Clear)  # 此时画笔为清除功能，可以清除已有像素
            # p.drawLine(self.mapFromGlobal(self._last_pressed_mouse_pos),
            #            self.mapFromGlobal(self._current_pressed_mouse_pos))  # 从哪里绘制到哪里,当使用event.pos()时可以不用mapFromGlobal
            #直接绘制点间距太大，下面部分使用增加点密度来达到抗锯齿
            space = 5/100#每个点出现的频率
            space_size = self._brush_size*space#每多少距离生成一个点
            pos_last = self.mapFromGlobal(self._last_pressed_mouse_pos)#移动起始点
            pos_current = self.mapFromGlobal(self._current_pressed_mouse_pos)#移动结束点
            x1, y1 = pos_last.x(), pos_last.y()#相对位置的起始坐标
            x2, y2 = pos_current.x(), pos_current.y()#相对位置的结束坐标
            length = ((x1-x2)**2 + (y1-y2)**2)**0.5#直角边平方和为斜边的平方
            count = length/space_size#这段距离要生成多少个点
            per_delta_pos = (QPointF(pos_current)-QPointF(pos_last))/count#每段距离的长度,返回的是QPoint类型：[int, int]
            poss = []
            for i in range(int(count)):
                poss.append(pos_last + per_delta_pos * i)#储存这段距离里要生的每个点所在的点位置
            if poss:
                if poss[-1] != pos_current:
                    poss.append(pos_current)#当最后一个点没取到结束点时，将结束点设为最后一个点
            else:
                poss = [pos_last, pos_current]#如果移动距离导致两点之间距离短到无法取画笔的5%距离，就直接将初始和结束点设为首尾两点

            brush_radius = QPointF(self._brush_size/2, self._brush_size/2)#将画笔半径组成一个QPoint
            for pos in poss:
                p.drawEllipse(QRectF(pos - brush_radius, pos + brush_radius))#绘制椭圆方法，将每个点的左上角到右下角点找到


            p.end()
            self._last_pressed_mouse_pos = self._current_pressed_mouse_pos  # 使起始位置为结束位置，让下次绘制从当前结束位置开始
        self.update()  # 不放在if外面就不能在鼠标在控件内时刷新圆圈在控件中的位置

    def mouseReleaseEvent(self, event):  # 松开
        if event.button() == Qt.LeftButton:
            self._is_drawing = False
            self._last_pressed_mouse_pos = None
            self._current_pressed_mouse_pos = None

    def dragEnterEvent(self, event):
        path = event.mimeData().text()
        path = path[8:]#去掉字符串最前面的‘file:///’
        if os.path.exists(path) and os.path.splitext(path)[1] in ['.jpg', '.png', '.bmp']:
            event.accept()
        else:
            print('拖入文件格式不对。')
            event.ignore()

    def dropEvent(self, event):
        picture = event.mimeData().text()
        path = picture[8:]
        pix = QPixmap(path)
        p = QPainter()
        p.begin(self._canvas)

        pix_center = QPoint(pix.width()//2, pix.height()//2)#这里普通相除会返回浮点，但QPoint需要int
        p.drawPixmap(QRect(event.pos()-pix_center, event.pos()+pix_center), pix)#在以鼠标位置为中心的位置，图片宽高的范围内绘制pix

        p.end()
        self.update()

    def set_tool(self, tool):
        self._tool = tool

    def get_brush_size(self):
        return self._brush_size

    def set_brush_size(self, size):
        self._brush_size = self._brush_size + size
        self.update()

    def get_brush_color(self):
        return self._brush_color

    def set_brush_color(self, color):
        self._brush_color = color

    def get_canvas(self):
        return self._canvas


class ToolBar(QWidget):
    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)
        self.but_setColor = QPushButton('设置颜色')
        self.but_save = QPushButton('保存')

        self.rdo_brush = QRadioButton('画笔')
        self.rdo_brush.setChecked(True)
        self.rdo_rubber = QRadioButton('橡皮')

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.but_setColor)
        main_layout.addWidget(self.rdo_brush)
        main_layout.addWidget(self.rdo_rubber)
        main_layout.addWidget(self.but_save)
        main_layout.addStretch()

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(Qt.gray))
        p.drawRect(self.rect())

        p.end()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.setWindowIcon(QIcon('asFace.png'))
        self.resize(800, 600)

        self.board = Board()
        self.toolBar = ToolBar()

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.board)
        main_layout.addWidget(self.toolBar)

        self.toolBar.but_setColor.clicked.connect(self.set_brush_color)
        self.toolBar.but_save.clicked.connect(self.save_pix)
        self.toolBar.rdo_brush.clicked.connect(lambda :self.set_brush('brush'))
        self.toolBar.rdo_rubber.clicked.connect(lambda :self.set_brush('reaser'))

    def set_brush_color(self):
        color = QColorDialog.getColor(self.board.get_brush_color())
        if color.isValid():
            self.board.set_brush_color(color)

    def set_brush(self, tool):
        if tool == 'brush':
            self.board.set_tool(tool)
        elif tool == 'reaser':
            self.board.set_tool(tool)

    def save_pix(self):
        pix = self.board._canvas#该变量本不应该在外部直接调用，该使用self.board.get_canvas()方法，但直接用也可以运行
        path = QFileDialog.getSaveFileName(self, '保存当前绘图界面', os.path.dirname(__file__), ('images (*.png)'))
        if path[0]:
            pix.save(path[0], 'png', 100)#保存的路径，格式，质量


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.board.set_tool('brush')
            self.toolBar.rdo_brush.setChecked(True)
        elif event.key() == Qt.Key_W:
            self.board.set_tool('reaser')
            self.toolBar.rdo_rubber.setChecked(True)
        elif event.key() == Qt.Key_Up:
            self.board.set_brush_size(5)
        elif event.key() == Qt.Key_Down:
            self.board.set_brush_size(-5)


if __name__ == '__main__':  # __name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    # sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
