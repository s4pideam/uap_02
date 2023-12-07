from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextCursor


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        
        self.functionFormat = QTextCharFormat()
        self.functionFormat.setForeground(QColor(255,184,108 )) #orange
        self.functionPattern = QRegularExpression(r'\b((?!(if|else|while|do|then)\s*\()(\w+))\s*(?=\()')

        self.operatorFormat = QTextCharFormat()
        self.operatorFormat.setForeground(QColor(255,85,85 ))
        keywords = [
            r'\+', r'-', r'\*', r'\\', r'>' , r'<' , r'='
        ]
        self.operatorPattern = [r'%s' % keyword for keyword in keywords]
	
        
        self.constFormat = QTextCharFormat()
        self.constFormat.setForeground(QColor(189,147,249))
        keywords = [
            'true', 'false'
        ]
        self.constPattern = [r'\b%s\b' % keyword for keyword in keywords]

        
        self.atomicFormat = QTextCharFormat()
        self.atomicFormat.setForeground(QColor(255,121,198))
        self.atomicFormat.setFontWeight(QFont.Bold)
        keywords = [
            'let', 'in'
        ]
        self.atomicPattern = [r'\b%s\b' % keyword for keyword in keywords]

        
        self.keywordFormat = QTextCharFormat()
        self.keywordFormat.setForeground(QColor(33, 150, 243))
        keywords = [
            'if', 'else', 'then'
        ]
        self.keywordPattern = [r'\b%s\b' % keyword for keyword in keywords]


        self.loopFormat = QTextCharFormat()
        self.loopFormat.setForeground(QColor(241, 250, 140))
        keywords = [
            'while', 'do'
        ]
        self.loopPattern = [r'\b%s\b' % keyword for keyword in keywords]

        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(QColor(76, 175, 80))
        self.commentPattern = QRegularExpression(r'//[^\n]*')

    def highlightBlock(self, text):
        for pattern, format in [(self.commentPattern, self.commentFormat)] + [(QRegularExpression(pattern), self.keywordFormat) for pattern in self.keywordPattern] + [(QRegularExpression(pattern), self.atomicFormat) for pattern in self.atomicPattern] + [(QRegularExpression(pattern), self.constFormat) for pattern in self.constPattern] + [(self.functionPattern, self.functionFormat)] + [(QRegularExpression(pattern), self.operatorFormat) for pattern in self.operatorPattern]  + [(QRegularExpression(pattern), self.loopFormat) for pattern in self.loopPattern]:
            matchIterator = pattern.globalMatch(text)
            while matchIterator.hasNext():
                match = matchIterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

                
    def underline_red(self, pos):
        cursor = QTextCursor(self.document())
        cursor.setPosition(pos)
        cursor.setPosition(pos + 1, QTextCursor.KeepAnchor)
        
        format = QTextCharFormat()
        format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        format.setUnderlineColor(QColor(255, 85, 85))
        
        cursor.mergeCharFormat(format)

    def clear_all_underlines(self):
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.Document)
    
        format = QTextCharFormat()
        format.setUnderlineStyle(QTextCharFormat.NoUnderline)
    
        cursor.mergeCharFormat(format)
