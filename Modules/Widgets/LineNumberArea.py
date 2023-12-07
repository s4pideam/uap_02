import sys

from PySide6.QtCore import QRect, QSize, Qt, QEvent
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QWidget


class LineNumberArea(QWidget):
    def __init__(self, textEdit):
        super().__init__(textEdit)
        self.textEdit = textEdit
        self.setFont(QFont("Monospace"))
        self.setMinimumWidth(self.fontMetrics().horizontalAdvance('99'))

        self.textEdit.blockCountChanged.connect(self.updateTextViewport)
        self.textEdit.updateRequest.connect(self.updateViewport)
        self.textEdit.installEventFilter(self)
        self.updateTextViewport(0)
        self.target_lines = []

    def getTargetLines(self):
        return self.target_lines
    
    def setTargetLines(self,lines):
        self.target_lines = lines
        self.update()

    
    def sizeHint(self):
        return QSize(self.getMaxWidth(), 0)

    def paintEvent(self, event):
        self.lineNumberAreaPaintEvent(event)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#282a36"))
        block = self.textEdit.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.textEdit.blockBoundingGeometry(block).translated(self.textEdit.contentOffset()).top()
        bottom = top + self.textEdit.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.white)
                painter.drawText(QRect(10, top, self.getMaxWidth()-5, self.textEdit.fontMetrics().boundingRect(number).height()), Qt.AlignLeft, number)
                if blockNumber + 1 in self.target_lines:
                    border_width = 2
                    painter.fillRect(QRect(self.getMaxWidth() - border_width, top+3, border_width, self.textEdit.fontMetrics().boundingRect(number).height()), QColor("#ff2a36"))
            block = block.next()
            top = bottom
            bottom = top + self.textEdit.blockBoundingRect(block).height()
            blockNumber += 1

    def eventFilter(self, obj, event):
        if obj == self.textEdit and event.type() == QEvent.Resize:
            cr = self.textEdit.contentsRect()
            self.setGeometry(QRect(cr.left(), cr.top(), self.getMaxWidth(), cr.height()))
        return super().eventFilter(obj, event)
    
    def getMaxWidth(self):
        l = len(str(max(99, self.textEdit.blockCount())))
        return 30 + self.textEdit.fontMetrics().horizontalAdvance('9') * l

    def updateTextViewport(self, _):
        self.textEdit.setViewportMargins(self.getMaxWidth() + 5, 0, 0, 0)

    def updateViewport(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.getMaxWidth(), rect.height())

        if rect.contains(self.textEdit.viewport().rect()):
            self.updateTextViewport(0)
