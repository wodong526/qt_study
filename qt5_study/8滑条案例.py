import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class myLineEdit(QLineEdit):
    valueSig = pyqtSignal(float)
    def __init__(self, parent):
        super(myLineEdit, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)  #设置文本显示位置为中间
        self.hide()
        self._value = None

        self.editingFinished.connect(self.on_finished)#点击回车或者输入框失去焦点就触发

        validator = QDoubleValidator(self)#生成浮点验证器
        validator.setRange(0, 100)#验证器范围
        validator.setNotation(QDoubleValidator.StandardNotation)
        #小数位的书写方法，当前为正常书写方式，ScientificNotation类型会以携带E的指数书写方式
        validator.setDecimals(2)#浮点精确位数
        self.setValidator(validator)
        #验证器也能写成下面这样，区别是上面的还无法限制到最大值为100，只能限制整数部分为三位数，
        # 下面的方法不能限制最大值，但由于不能输入-号所以最小值为0，且小数位也没法精确
        # validator = QRegExpValidator(parent)
        # validator.setRegExp(QRegExp('[0-9.]+'))
        # self.setValidator(validator)

    def set_value(self, val):
        self._value = str(val)#需要将内容转正str才能被填入
        self.setText(self._value)
        self.selectAll()#选中文本框中的所有内容
        self.setFocus()#使该控件获得焦点
        self.show()

    def on_finished(self):
        #结束编辑，隐藏控件
        self.hide()
        self.valueSig.emit(float(self.text()))

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.on_finished()
        else:
            super(myLineEdit, self).keyReleaseEvent(event)


class mySlider(QWidget):
    def __init__(self, parent):
        super(mySlider, self).__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)#将该控件的获取焦点方式设置为点击获取焦点
        self._value = 0
        self._min_value = 0
        self._max_value = 100
        self._last_pressed_mouse_pos = None
        self._current_pressed_mouse_pos = None
        self._is_value_changing = False#是否正在更改

        self._lin_value = myLineEdit(self)
        self._lin_value.valueSig.connect(self.set_value)

    def get_value(self):
        return self._value

    def set_value(self, val):
        val = round(val, 2)#将过长的小数位精确到小数点后两位
        if val >= 100:
            self._value = 100
        elif val <=0:
            self._value = 0
        else:
            self._value = val

        self.update()


    def paintEvent(self, event):
        p = QPainter()
        pix = QPixmap(self.size())#把显示的东西画在pix上，再将pix画在控件上。因为pix可以设置透明属性，否则清除掉像素的圆角会是原本的黑色底
        pix.fill(Qt.transparent)#设置为透明

        p.begin(pix)
        p.setRenderHint(QPainter.Antialiasing, True)

        #灰色底色
        p.setPen(Qt.NoPen)
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(QColor(200, 200, 200))
        p.setBrush(brush)
        p.drawRect(self.rect())

        #进度条
        p.setPen(Qt.NoPen)
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(QColor(40, 150, 200))
        p.setBrush(brush)
        p.drawRect(QRect(0, 0, self.width()*int(self._value)//self._max_value, self.height()))#从0,0到控件宽的现有值的比例

        #绘制渐变光亮
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, QColor(255, 255, 255, 200))#在全长的百分之几的位置上绘制的颜色,最后一个数是透明度，完全透明为255
        g.setColorAt(0.2, QColor(255, 255, 255, 160))
        g.setColorAt(0.45, QColor(255, 255, 255, 80))
        g.setColorAt(0.451, QColor(0, 0, 0, 0))

        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawRect(self.rect())

        #滑条数值
        font = QFont()
        font.setPixelSize(self.height()//2)
        font.setFamily('微软雅黑')
        p.setFont(font)

        #字符
        pen = QPen(Qt.SolidLine)
        pen.setColor(QColor(0, 0, 0))
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        #p.drawText(self.rect(), Qt.AlignCenter, str(self.get_value()))#使用这个不会一直保持小数位存在的状态
        p.drawText(self.rect(), Qt.AlignCenter, '{:.2f}'.format(self.get_value()))

        #圆角外观，深色底
        r = 20#圆角的半径
        pen = QPen()
        pen.setColor(QColor(150, 150, 150))
        pen.setWidth(5)#圆角线宽
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(self.rect(), r, r)#绘制圆角矩形，在x和y上的圆角半径都为20

        #浅色顶
        pen = QPen()
        pen.setColor(QColor(200, 200, 200))
        pen.setWidth(3)  #圆角线宽
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(self.rect(), r, r)  #绘制圆角矩形，在x和y上的圆角半径都为20

        #去除圆角外的像素
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.red)

        # path = QPainterPath()#手写时这样，做列表for就下面那样
        # path.moveTo(0, 0)  #从控件的0,0坐标开始
        # path.lineTo(r, 0)  #绘制路径，先走直线到此点
        # path.arcTo(QRectF(0, 0, r * 2, r * 2), 90, 90)#从圆心旋转90度位置点到再加90度（180度）位置点经过的路线
        # path.closeSubpath()  #将绘制的路径封口，自动将末端点与起始点连接形成一个封闭形状
        # p.drawPath(path)  #清除这个形状内的像素
        w = self.width()
        h = self.height()
        center_lis = [(0, 0), (w, 0), (w, h), (0, h)]
        line_lis = [(r, 0), (w, r), (w-r, h), (0, h-r)]
        arc_center_lis = [(0, 0), (w-r*2, 0), (w-r*2, h-r*2), (0, h-r*2), ]
        rotato_lis = [(90, 90), (0, 90), (270, 90), (180, 90)]
        for i in range(len(center_lis)):
            path = QPainterPath()
            path.moveTo(center_lis[i][0], center_lis[i][1])
            path.lineTo(line_lis[i][0], line_lis[i][1])
            path.arcTo(QRectF(arc_center_lis[i][0], arc_center_lis[i][1], r*2, r*2), rotato_lis[i][0], rotato_lis[i][1])
            path.closeSubpath()
            p.drawPath(path)

        p.end()

        p.begin(self)
        p.drawPixmap(self.rect(),pix)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_value_changing = True
            self._last_pressed_mouse_pos = QCursor.pos()
            self._current_pressed_mouse_pos = QCursor.pos()

    def mouseMoveEvent(self, event):
        if self._is_value_changing:
            self.setCursor(Qt.SizeHorCursor)#将鼠标显示设置为横向双箭头
            self._current_pressed_mouse_pos = QCursor.pos()
            #delta = self._current_pressed_mouse_pos.x() - self._last_pressed_mouse_pos.x()
            screen_width = QDesktopWidget().screenGeometry(0).width()#获取屏幕，获取第一个屏幕（有多个屏幕依次类推1、2、3），获取屏幕的宽
            delta = (self._max_value - self._min_value)/screen_width*\
                    (self._current_pressed_mouse_pos.x() - self._last_pressed_mouse_pos.x())

            if event.modifiers() == Qt.ShiftModifier:#按住shift时数值微调
                self.set_value(self._value + delta*0.1)
            else:
                self.set_value(self._value + delta)

            self._last_pressed_mouse_pos = self._current_pressed_mouse_pos
            #self.update()#因为设置value时就会刷新显示，所以这里可以不用重复刷新

            #鼠标穿透屏幕
            pos_x = QCursor.pos().x()
            main_screen_gro = QDesktopWidget().screenGeometry(0)#QtCore.QRect()对象的四个元素的元组（0， 0， width，height）
            left = main_screen_gro.x()#最左侧，为0
            right = main_screen_gro.width() - 1#（0,0）是第一个像素，200像素宽的屏幕最后一颗像素为（199,0）
            if pos_x <= left:
                QCursor.setPos(right-1, QCursor.pos().y())
                self._last_pressed_mouse_pos = QCursor.pos()#当鼠标穿过屏幕后，起始点不能再为上一次移动的结束点，应从头开始为现在的位置
            elif pos_x >= right:
                QCursor.setPos(left+1, QCursor.pos().y())
                self._last_pressed_mouse_pos = QCursor.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ArrowCursor)#将鼠标显示设置为正常形状
            self._is_value_changing = False
            self._last_pressed_mouse_pos = None
            self._current_pressed_mouse_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.RightButton:
            self.set_value(0)
        elif event.button() == Qt.LeftButton:
            self.set_value(100)
        elif event.button() == Qt.MiddleButton:  #当双击中键时显示
            self._lin_value.set_value(self._value)

    def resizeEvent(self, event):
        #每当窗口发生伸缩变化时都会触发这个函数
        self._lin_value.resize(int(self.width()*0.8), int(self.height()*0.8))
        self._lin_value.move(int(self.width()*0.1), int(self.height()*0.1))

        font = QFont()
        font.setFamily('微软雅黑')
        font.setPixelSize(int(self.height()/2))
        self._lin_value.setFont(font)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(800, 600)
        self.setFocusPolicy(Qt.ClickFocus)  #将该控件的获取焦点方式设置为点击获取焦点

        self.slider = mySlider(self)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.slider)

if __name__ == '__main__':#__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())