# -*- coding: utf-8 -*-
# @Time    : 2019/9/1 15:09
# @Author  : Suyin
# @Email   : 820390693@qq.com
# @File    : main.py
# @Software: PyCharm


import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


def toRectF(rect):
    return QRectF(
        rect.x(),
        rect.y(),
        rect.width(),
        rect.height()
    )


def toRect(rectF):
    return QRect(
        rectF.x(),
        rectF.y(),
        rectF.width(),
        rectF.height()
    )


def normalizeRect(rect):
    x = rect.x()
    y = rect.y()
    w = rect.width()
    h = rect.height()
    if w < 0:
        x = x + w
        w = -w
    if h < 0:
        y = y + h
        h = -h
    return QRectF(x, y, w, h)


class WScreenshot(QWidget):
    u"""
    截图
    """
    REASON_CENTER,REASON_OTHER = range(2)
    pixmapGot = pyqtSignal(QPixmap, int)
    instance = None

    def __init__(self, parent = None):
        super(WScreenshot, self).__init__()
        self._parent = parent
        # self.saveDir = u'D:/'
        # self.saveName = u'W截图_{}'.format(QDateTime().currentDateTime().toString("yyyyMMdd_hh-mm-ss"))
        # self.saveFormat = 'JPG'
        # self.picQuality = 100
        # self.setWindowTitle(u'截图窗体')

        # self.setWindowFlag(Qt.Tool, True)
        # self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        # self.setWindowFlag(Qt.FramelessWindowHint, True)

        self.setWindowFlags(self.windowFlags() |Qt.Tool| Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # self.showFullScreen()  # 全屏显示
        self.setFixedSize(QDesktopWidget().screenGeometry(0).size())

        # 屏幕 和 屏幕信息
        self.screen = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
        self.screenSize = self.screen.rect().size()
        self.screenRect = toRectF(self.screen.rect())
        # -点
        self.screenTopLeft = self.screenRect.topLeft()
        self.screenBottomLeft = self.screenRect.bottomLeft()
        self.screenTopRight = self.screenRect.topRight()
        self.screenBottomRight = self.screenRect.bottomRight()
        # -上下左右限
        self.screenLeft = self.screenRect.left()
        self.screenRight = self.screenRect.right()
        self.screenTop = self.screenRect.top()
        self.screenBottom = self.screenRect.bottom()

        # A:start(x,y)        D:(x+w,y)
        #     -----------------
        #     |               |
        #     |               |
        #     -----------------
        # B:(x,y+h)           C:end(x+w,y+h)

        # 设置 self.screen 为窗口背景
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(self.screen))
        self.setPalette(palette)

        # 调节器层
        self.adjustment_original = QPixmap(self.screenSize)  # 初始调节器
        self.adjustment_original.fill(QColor(0, 0, 0, 64))
        self.adjustment = QPixmap()  # 调节器
        # self.adjustment = self.adjustment_original.copy()  # 调节器

        # 画布层
        self.canvas_original = QPixmap(self.screenSize)  # 初始画布
        self.canvas_original.fill(Qt.transparent)
        self.canvas_saved = self.canvas_original.copy()  # 保存已经画好的图案
        self.canvas = QPixmap()  # 画布

        # self.canvas = self.canvas_original.copy()  # 画布
        # self.canvas_saved = self.canvas.copy()
        # 输出
        self.output = QPixmap()

        # 当前功能状态
        self.isMasking = False
        self.hasMask = False
        self.isMoving = False
        self.isAdjusting = False
        self.isDrawing = False
        self.hasPattern = False
        self.mousePos = ''
        self.isShifting = False

        # 蒙版 和 蒙版信息
        self.maskRect = QRectF()
        self.maskRect_backup = QRectF()

        # 以下 16 个变量随self.maskRect变化而变化
        self.maskTopLeft = QPoint()
        self.maskBottomLeft = QPoint()
        self.maskTopRight = QPoint()
        self.maskBottomRight = QPoint()
        self.maskTopMid = QPoint()
        self.maskBottomMid = QPoint()
        self.maskLeftMid = QPoint()
        self.maskRightMid = QPoint()

        self.rectTopLeft = QRectF()
        self.rectBottomLeft = QRectF()
        self.rectTopRight = QRectF()
        self.rectBottomRight = QRectF()
        self.rectTop = QRectF()
        self.rectBottom = QRectF()
        self.rectLeft = QRectF()
        self.rectRight = QRectF()

        self.adjustmentLineWidth = 2
        self.adjustmentWhiteDotRadius = 6
        self.adjustmentBlueDotRadius = 4
        self.blue = QColor(200, 80, 80)
        self.setCursor(Qt.CrossCursor)  # 设置鼠标样式 十字

        self.setMouseTracking(True)

        # 鼠标事件点
        self.start = QPoint()
        self.end = QPoint()

        # self.test()

    def parent(self):
        return self._parent

    @classmethod
    def run(cls):
        cls.instance = cls()
        cls.instance.show()

    @classmethod
    def getPixmapGot(cls):
        return cls.instance.pixmapGot

    def test(self):
        self.hasMask = True
        self.isMasking = False
        self.maskRect = QRectF(100, 100, 600, 800)
        self.updateMaskInfo()
        self.update()

    def toMask(self):
        rect = QRectF(self.start, self.end)

        if self.isShifting:
            x = rect.x()
            y = rect.y()
            w = rect.width()
            h = rect.height()
            absW = abs(w)
            absH = abs(h)
            wIsLonger = True if absW > absH else False
            if w > 0:
                if h > 0:
                    end = QPoint(x + absW, y + absW) if wIsLonger else QPoint(x + absH, y + absH)
                else:
                    end = QPoint(x + absW, y - absW) if wIsLonger else QPoint(x + absH, y - absH)
            else:
                if h > 0:
                    end = QPoint(x - absW, y + absW) if wIsLonger else QPoint(x - absH, y + absH)
                else:
                    end = QPoint(x - absW, y - absW) if wIsLonger else QPoint(x - absH, y - absH)

            rect = QRectF(self.start, end)

        self.maskRect = QRectF(
            rect.x() + min(rect.width(), 0),
            rect.y() + min(rect.height(), 0),
            abs(rect.width()),
            abs(rect.height())
        )

        # 修正超出屏幕、碰撞
        if self.isShifting:
            self.fixCollision()

        self.updateMaskInfo()
        self.update()

    # 修复碰撞。针对 isShifting 的情况
    def fixCollision(self):
        vector = self.end - self.start
        vX = vector.x()
        vY = vector.y()
        resStart = self.maskRect.topLeft()
        resEnd = self.maskRect.bottomRight()
        mLeft = self.maskRect.left()
        mRight = self.maskRect.right()
        mTop = self.maskRect.top()
        mBottom = self.maskRect.bottom()
        # w < h
        if self.maskRect.left() <= self.screenLeft:
            newW = mRight - self.screenLeft
            if vY > 0:
                resStart = QPoint(self.screenLeft, mTop)
                resEnd = resStart + QPoint(newW, newW)
            else:
                resStart = resEnd + QPoint(-newW, -newW)
        elif self.maskRect.right() >= self.screenRight:
            newW = self.screenRight - mLeft
            if vY > 0:
                resEnd = resStart + QPoint(newW, newW)
            else:
                resEnd = QPoint(self.screenRight, mBottom)
                resStart = resEnd + QPoint(-newW, -newW)
        # w > h
        elif self.maskRect.top() <= self.screenTop:
            newW = mBottom - self.screenTop
            if vX > 0:
                resStart = QPoint(mLeft, self.screenTop)
                resEnd = resStart + QPoint(newW, newW)
            else:
                resStart = resEnd + QPoint(-newW, -newW)
        elif self.maskRect.bottom() >= self.screenBottom:
            newW = self.screenBottom - mTop
            if vX > 0:
                resEnd = resStart + QPoint(newW, newW)
            else:
                resEnd = QPoint(mRight, self.screenBottom)
                resStart = resEnd + QPoint(-newW, -newW)
        self.maskRect = QRectF(resStart, resEnd)

    def toAdjust(self):

        mRect = self.maskRect_backup
        mStart = mRect.topLeft()
        mStartX = mStart.x()
        mStartY = mStart.y()
        mEnd = mRect.bottomRight()
        mEndX = mEnd.x()
        mEndY = mEnd.y()
        resStart = mStart
        resEnd = mEnd
        if not self.isShifting:

            if self.mousePos == 'TL':
                resStart = self.end
            elif self.mousePos == 'BL':
                resStart = QPoint(self.end.x(), mStartY)
                resEnd = QPoint(mEndX, self.end.y())
            elif self.mousePos == 'TR':
                resStart = QPoint(mStartX, self.end.y())
                resEnd = QPoint(self.end.x(), mEndY)
            elif self.mousePos == 'BR':
                resEnd = self.end
            elif self.mousePos == 'T':
                resStart = QPoint(mStartX, self.end.y())
            elif self.mousePos == 'B':
                resEnd = QPoint(mEndX, self.end.y())
            elif self.mousePos == 'L':
                resStart = QPoint(self.end.x(), mStartY)
            elif self.mousePos == 'R':
                resEnd = QPoint(self.end.x(), mEndY)
        else:
            # print(self.mousePos)
            if self.mousePos == 'T':
                resStart = QPoint(mStartX, self.end.y())
                newW = mEndY - self.end.y()
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'B':
                newW = self.end.y() - mStartY
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'L':
                resStart = QPoint(self.end.x(), mStartY)
                newW = mEndX - self.end.x()
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'R':
                newW = self.end.x() - mStartX
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'TL':
                newW = mEndX - self.end.x()
                newH = mEndY - self.end.y()
                newW = newW if newW > newH else newH
                resStart = resEnd + QPoint(-newW, -newW)
            elif self.mousePos == 'BR':
                newW = self.end.x() - mStartX
                newH = self.end.y() - mStartY
                newW = newW if newW > newH else newH
                resEnd = resStart + QPoint(newW, newW)
            elif self.mousePos == 'TR':
                newW = self.end.x() - mStartX
                newH = mEndY - self.end.y()
                newW = newW if newW > newH else newH
                resStart = mRect.bottomLeft()
                resEnd = resStart + QPoint(newW, -newW)
            elif self.mousePos == 'BL':
                newW = mEndX - self.end.x()
                newH = self.end.y() - mStartY
                newW = newW if newW > newH else newH
                resStart = mRect.topRight()
                resEnd = resStart + QPoint(-newW, newW)

        self.maskRect = normalizeRect(QRectF(resStart, resEnd))

        self.fixCollision()

        self.updateMaskInfo()
        self.update()

    def toMove(self):
        mStart = self.maskRect_backup.topLeft()
        mStartX = mStart.x()
        mStartY = mStart.y()
        mEnd = self.maskRect_backup.bottomRight()
        mEndX = mEnd.x()
        mEndY = mEnd.y()
        mWidth = self.maskRect_backup.width()
        mHeight = self.maskRect_backup.height()
        mWHPoint = QPoint(mWidth, mHeight)
        vector = self.end - self.start
        vX = vector.x()
        vY = vector.y()

        resStart = mStart + vector
        resStartX = resStart.x()
        resStartY = resStart.y()
        resEnd = mEnd + vector
        resEndX = resEnd.x()
        resEndY = resEnd.y()

        if resStartX <= self.screenLeft and resStartY <= self.screenTop:
            resStart = self.screenTopLeft
            resEnd = resStart + mWHPoint
        elif resEndX >= self.screenRight and resEndY >= self.screenBottom:
            resEnd = self.screenBottomRight
            resStart = resEnd - mWHPoint
        elif resStartX <= self.screenLeft and resEndY >= self.screenBottom:
            resStart = QPoint(self.screenLeft, self.screenBottom - mHeight)
            resEnd = resStart + mWHPoint
        elif resEndX >= self.screenRight and resStartY <= self.screenTop:
            resStart = QPoint(self.screenRight - mWidth, self.screenTop)
            resEnd = resStart + mWHPoint
        elif resStartX <= self.screenLeft:
            resStart = QPoint(self.screenLeft, mStartY + vY)
            resEnd = resStart + mWHPoint
        elif resStartY <= self.screenTop:
            resStart = QPoint(mStartX + vX, self.screenTop)
            resEnd = resStart + mWHPoint
        elif resEndX >= self.screenRight:
            resEnd = QPoint(self.screenRight, mEndY + vY)
            resStart = resEnd - mWHPoint
        elif resEndY >= self.screenBottom:
            resEnd = QPoint(mEndX + vX, self.screenBottom)
            resStart = resEnd - mWHPoint
        self.maskRect = normalizeRect(QRectF(resStart, resEnd))
        self.updateMaskInfo()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()
            self.end = self.start
            if self.hasMask:
                self.maskRect_backup = self.maskRect
                if self.mousePos == 'mask':
                    self.isMoving = True
                else:
                    self.isAdjusting = True
            else:
                self.isMasking = True

        if event.button() == Qt.RightButton:
            if self.isMasking or self.hasMask:
                self.isMasking = False
                self.hasMask = False
                self.maskRect = QRectF(0, 0, 0, 0)
                self.updateMaskInfo()
                self.update()
            else:
                self.close()

    def closeEvent(self, event):
        self.deleteLater()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isMasking = False
            self.isMoving = False
            self.isAdjusting = False
            self.isDrawing = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mousePos == 'mask':
                self.save(reason = self.REASON_CENTER)
                self.close()
            else:
                self.save(reason =self.REASON_OTHER)
                self.close()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        self.end = pos

        if self.isMasking:
            self.hasMask = True
            self.toMask()
        elif self.isMoving:
            self.toMove()
        elif self.isAdjusting:
            self.toAdjust()

        # 设置鼠标样式
        if self.isDrawing:
            pass
        else:
            if self.hasMask:
                if self.isMoving:
                    self.setCursor(Qt.SizeAllCursor)
                elif self.isAdjusting:
                    pass
                else:
                    self.setMouseShape(pos)
            else:
                self.mousePos = ''
                self.setCursor(Qt.CrossCursor)  # 设置鼠标样式 十字

    def setMouseShape(self, pos):
        # 设置鼠标样式
        if self.rectTopLeft.contains(pos):
            self.setCursor(Qt.SizeFDiagCursor)
            self.mousePos = 'TL'
        elif self.rectBottomLeft.contains(pos):
            self.setCursor(Qt.SizeBDiagCursor)
            self.mousePos = 'BL'
        elif self.rectBottomRight.contains(pos):
            self.setCursor(Qt.SizeFDiagCursor)
            self.mousePos = 'BR'
        elif self.rectTopRight.contains(pos):
            self.setCursor(Qt.SizeBDiagCursor)
            self.mousePos = 'TR'
        elif self.rectLeft.contains(pos):
            self.setCursor(Qt.SizeHorCursor)
            self.mousePos = 'L'
        elif self.rectTop.contains(pos):
            self.setCursor(Qt.SizeVerCursor)
            self.mousePos = 'T'
        elif self.rectBottom.contains(pos):
            self.setCursor(Qt.SizeVerCursor)
            self.mousePos = 'B'
        elif self.rectRight.contains(pos):
            self.setCursor(Qt.SizeHorCursor)
            self.mousePos = 'R'
        elif self.maskRect.contains(pos):
            self.setCursor(Qt.SizeAllCursor)
            self.mousePos = 'mask'

    def updateMaskInfo(self):
        # 蒙版点
        self.maskTopLeft = self.maskRect.topLeft()
        self.maskBottomLeft = self.maskRect.bottomLeft()
        self.maskTopRight = self.maskRect.topRight()
        self.maskBottomRight = self.maskRect.bottomRight()
        self.maskTopMid = (self.maskTopLeft + self.maskTopRight) / 2
        self.maskBottomMid = (self.maskBottomLeft + self.maskBottomRight) / 2
        self.maskLeftMid = (self.maskTopLeft + self.maskBottomLeft) / 2
        self.maskRightMid = (self.maskTopRight + self.maskBottomRight) / 2
        # 除蒙版区外的 8 个区域
        self.rectTopLeft = QRectF(self.screenTopLeft, self.maskTopLeft)
        self.rectBottomLeft = QRectF(self.screenBottomLeft, self.maskBottomLeft)
        self.rectTopRight = QRectF(self.screenTopRight, self.maskTopRight)
        self.rectBottomRight = QRectF(self.screenBottomRight, self.maskBottomRight)
        self.rectTop = QRectF(QPoint(self.maskRect.left(), self.screenTop), self.maskTopRight)
        self.rectBottom = QRectF(self.maskBottomLeft, QPoint(self.maskRect.right(), self.screenBottom))
        self.rectLeft = QRectF(QPoint(self.screenLeft, self.maskRect.top()), self.maskBottomLeft)
        self.rectRight = QRectF(self.maskTopRight, QPoint(self.screenRight, self.maskRect.bottom()))

    def paintEvent(self, event):

        painter = QPainter()

        # 开始在 画布层 上绘画。如果正在绘画，绘制图案, 否则不绘制
        if self.isDrawing:
            if self.hasPattern:
                self.canvas = self.canvas_saved.copy()
            else:
                self.canvas = self.canvas_original.copy()
            painter.begin(self.canvas)
            self.paintCanvas(painter)
            painter.end()
            # 把 画布层 绘画到窗口上
            painter.begin(self)
            painter.drawPixmap(self.screenRect, self.canvas)
            painter.end()

        # 开始在 空白调节器层 上绘画。如果有蒙版，绘制调节器形状, 否则不绘制
        else:
            self.adjustment = self.adjustment_original.copy()
            painter.begin(self.adjustment)
            self.paintAdjustment(painter)
            painter.end()
            # 把 调节器层 绘画到窗口上
            painter.begin(self)
            painter.drawPixmap(toRect(self.screenRect), self.adjustment)
            painter.end()

    def paintAdjustment(self, painter):
        if self.hasMask:
            painter.setRenderHint(QPainter.Antialiasing, True)  # 反走样
            painter.setPen(Qt.NoPen)
            # 在蒙版区绘制屏幕背景
            painter.setBrush(QBrush(self.screen))
            painter.drawRect(self.maskRect)
            # 绘制线框
            lineWidth = self.adjustmentLineWidth
            painter.setBrush(self.blue)
            painter.drawRect(
                QRectF(
                    self.maskTopLeft + QPoint(-lineWidth, -lineWidth),
                    self.maskTopRight + QPoint(lineWidth, 0))
            )
            painter.drawRect(
                QRectF(
                    self.maskBottomLeft + QPoint(-lineWidth, 0),
                    self.maskBottomRight + QPoint(lineWidth, lineWidth)
                )
            )
            painter.drawRect(
                QRectF(
                    self.maskTopLeft + QPoint(-lineWidth, -lineWidth),
                    self.maskBottomLeft + QPoint(0, lineWidth)
                )
            )
            painter.drawRect(
                QRectF(
                    self.maskTopRight + QPoint(0, -lineWidth),
                    self.maskBottomRight + QPoint(lineWidth, lineWidth)
                )
            )
            if self.maskRect.width() >= 150 and self.maskRect.height() >= 150:
                # 绘制点
                points = [
                    self.maskTopLeft, self.maskTopRight, self.maskBottomLeft, self.maskBottomRight,
                    self.maskLeftMid, self.maskRightMid, self.maskTopMid, self.maskBottomMid
                ]
                # -白点
                whiteDotRadiusPoint = QPoint(self.adjustmentWhiteDotRadius, self.adjustmentWhiteDotRadius)
                painter.setBrush(Qt.white)
                for point in points:
                    painter.drawEllipse(QRectF(point - whiteDotRadiusPoint, point + whiteDotRadiusPoint))
                # -蓝点
                blueDotRadius = QPoint(self.adjustmentBlueDotRadius, self.adjustmentBlueDotRadius)
                painter.setBrush(self.blue)
                for point in points:
                    painter.drawEllipse(QRectF(point - blueDotRadius, point + blueDotRadius))

            # 绘制尺寸
            maskSize = (abs(int(self.maskRect.width())), abs(int(self.maskRect.height())))
            painter.setFont(QFont('Monaco', 7, QFont.Bold))
            painter.setPen(Qt.transparent)  # 透明获得字体Rect
            textRect = painter.drawText(
                QRectF(self.maskTopLeft.x() + 10, self.maskTopLeft.y() - 25, 100, 20),
                Qt.AlignLeft | Qt.AlignVCenter,
                '{} x {}'.format(*maskSize)
            )
            painter.setBrush(QColor(0, 0, 0, 128))  # 黑底
            padding = 5
            painter.drawRect(
                QRectF(
                    textRect.x() - padding,
                    textRect.y() - padding * 0.4,
                    textRect.width() + padding * 2,
                    textRect.height() + padding * 0.4
                )
            )
            painter.setPen(Qt.white)
            painter.drawText(
                textRect,
                Qt.AlignLeft | Qt.AlignVCenter,
                '{} x {}'.format(*maskSize)
            )
            painter.setPen(Qt.NoPen)

    def paintCanvas(self, painter):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # 大键盘、小键盘回车
            if self.hasMask:
                self.save(reason = self.REASON_OTHER)
            self.close()
        if event.modifiers() & Qt.ShiftModifier:
            self.isShifting = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.isShifting = False

    def save(self, reason):
        self.output = self.screen.copy()
        if self.hasPattern:
            painter = QPainter(self.output)
            painter.drawPixmap(self.canvas)
        self.output = self.output.copy(toRect(self.maskRect))

        self.pixmapGot.emit(self.output, reason)

        # self.output.save(
        #     u'{saveDir}/{saveName}.{format}'.format(
        #         saveDir = self.saveDir.rstrip('/'),
        #         saveName = self.saveName,
        #         format = self.saveFormat.lower()
        #     ),
        #     self.saveFormat,
        #     self.picQuality
        # )


if __name__ == '__main__':

    app = QApplication.instance() or QApplication(sys.argv)
    w = WScreenshot()
    w.show()
    app.exec_()
