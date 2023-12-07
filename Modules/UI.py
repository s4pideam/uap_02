import os
import sys
from PySide6.QtCore import QEasingCurve, QEvent, QFile, QIODevice, QPropertyAnimation, Qt, QIODevice, QTextStream, QDateTime
from PySide6.QtGui import QIcon, QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QListWidgetItem, QMainWindow, QSizeGrip, QAbstractItemView, QFileDialog
from Modules.Widgets import SyntaxHighlighter, LineNumberArea, DotViewer

from Modules.Tripla import TriplaYacc


QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
class PageIndex:
    Home = 0
    Code = 1
    Assembly = 2
    Tree = 3
    AstTree = 4

class MainWindow(QMainWindow):
    UI_FILE = "resources/main.ui"
    QSS_FILE = "resources/main.qss"
    HTML_FILE = "resources/home.html"
    ICON_RESTORE = QIcon("./resources/icons/restore.svg")
    ICON_MAXIMIZE = QIcon("./resources/icons/square.svg")
    ICON_FILE = QIcon("./resources/icons/file.svg")
    ICON_FILE_ACCENT = QIcon("./resources/icons/file_accent.svg")
    ANIMATION_DURATION = 500
    ANIMATION_EASING_CURVE = QEasingCurve.InOutQuart

    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.load_ui()
        self.load_styles()
        self.load_html_content()

        self.ui.WhatsNewContent.setText(self.html_content)

        self.setCentralWidget(self.ui)
        self.resize(self.ui.size())
        self.setup_connections()
        self.sizegrip = QSizeGrip(self.ui.Grip)
        self.sizegrip.resize(15, 15)
        self.ICON_FILE_SMALL = QIcon(self.ICON_FILE.pixmap(12, 12))
        self.ICON_FILE_SMALL_ACCENT = QIcon(self.ICON_FILE_ACCENT.pixmap(12, 12))
        self.setup_syntax_highlighting()
        self.setup_line_number_area()
        self.ui.ListStack.setSelectionMode(QAbstractItemView.NoSelection)
#        self.set_top(3)
        self.triplaYacc = TriplaYacc();
        self.dotViewer = DotViewer();
        self.AstdotViewer = DotViewer();
        self.ui.SvgViewer.addWidget(self.dotViewer)
        self.ui.AstSvgViewer.addWidget(self.AstdotViewer)



    def eventFilter(self, source, event):
        if  event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self.window().windowHandle().startSystemMove()
            event.accept()
            return True
        return super().eventFilter(source, event)

    def set_top(self, i):
        self.ui.ListStack.item(i).setForeground(QColor(255, 121, 198))

    def showEvent(self, event):
        super().showEvent(event)
        self.load_styles()



    def load_ui(self):
        loader = QUiLoader()
        ui_file = QFile(self.UI_FILE)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {self.UI_FILE}: {ui_file.errorString()}")
            sys.exit(-1)
        self.ui = loader.load(ui_file)
        ui_file.close()
        if not self.ui:
            print(loader.errorString())
            sys.exit(-1)

    def load_styles(self):
        style_sheet = self.load_file_content(self.QSS_FILE)
        self.ui.StyleSheet.setStyleSheet(style_sheet)

    def load_html_content(self):
        self.html_content = self.load_file_content(self.HTML_FILE)

    def load_file_content(self, file_name):
        file = QFile(file_name)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            print(f"Cannot open {file_name}: {file.errorString()}")
            sys.exit(-1)
        content = file.readAll().data().decode("utf-8")
        file.close()
        return content
    
        # Call the base class implementation to handle other events
        QLabel.mouseDoubleClickEvent(self.ui.Examples, event)
    def setup_connections(self):
        self.ui.Close.clicked.connect(self.close)
        self.ui.Minimize.clicked.connect(self.showMinimized)
        self.ui.Maximize.clicked.connect(self.toggle_maximized)
        
        self.ui.Home.clicked.connect(lambda: self.ui.Pages.setCurrentIndex(PageIndex.Home))
        self.ui.Code.clicked.connect(lambda: self.ui.Pages.setCurrentIndex(PageIndex.Code))
        self.ui.Assembly.clicked.connect(lambda: self.ui.Pages.setCurrentIndex(PageIndex.Assembly))
        self.ui.ParseTree.clicked.connect(lambda: self.ui.Pages.setCurrentIndex(PageIndex.Tree))
        self.ui.AstTree.clicked.connect(lambda: self.ui.Pages.setCurrentIndex(PageIndex.AstTree))
        self.ui.Hide.clicked.connect(self.toggle_nav)
        self.ui.Examples.clicked.connect(self.toggle_examples)
        self.ui.ExamplesClose.clicked.connect(self.toggle_examples)
        self.ui.Title.installEventFilter(self)
        self.ui.Logo.installEventFilter(self)
        self.ui.ExamplesHeader.installEventFilter(self)
        self.ui.ExamplesListView.itemDoubleClicked.connect(self.load_example)
        self.ui.Editor.setTabStopDistance(4 * self.ui.Editor.fontMetrics().horizontalAdvance(' '))
        self.ui.AssemblyEditor.setTabStopDistance(4 * self.ui.AssemblyEditor.fontMetrics().horizontalAdvance(' '))
        self.ui.CodeRun.clicked.connect(self.runCode)

        self.ui.TreeSave.clicked.connect(self.saveTree)
        self.ui.TreeZoomOut.clicked.connect(self.zoomOut)
        self.ui.TreeZoomReset.clicked.connect(self.zoomReset)
        self.ui.TreeZoomIn.clicked.connect(self.zoomIn)

        self.ui.AstTreeSave.clicked.connect(self.AstsaveTree)
        self.ui.AstTreeZoomOut.clicked.connect(self.AstzoomOut)
        self.ui.AstTreeZoomReset.clicked.connect(self.AstzoomReset)
        self.ui.AstTreeZoomIn.clicked.connect(self.AstzoomIn)


    def saveTree(self):
        options = QFileDialog.Options()
#        options |= QFileDialog.DontUseNativeDialog

        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Dot Files (*.dot)", options=options)

        if file_name:
            if not file_name.lower().endswith(".dot"):
                file_name += ".dot"
            self.write_to_file(file_name,self.dotViewer.dot_source)


    def AstsaveTree(self):
        options = QFileDialog.Options()
#        options |= QFileDialog.DontUseNativeDialog

        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Dot Files (*.dot)", options=options)

        if file_name:
            if not file_name.lower().endswith(".dot"):
                file_name += ".dot"
            self.write_to_file(file_name,self.AstdotViewer.dot_source)

    def write_to_file(self,file_path, content_to_write):
        file = QFile(file_path)

        if not file.open(QIODevice.WriteOnly | QIODevice.Text):
            print(f"Cannot open file {file_path} for writing.")
            return

        stream = QTextStream(file)
        stream << content_to_write


        file.close()
        print(f"Content written to {file_path}")
        
    def zoomOut(self):
        self.dotViewer.zoom_factor *= 0.8
        self.dotViewer.repaint()
    def zoomReset(self):
        self.dotViewer.zoom_factor = 1.0
        self.dotViewer.repaint()
    def zoomIn(self):
        self.dotViewer.zoom_factor *= 1.2
        self.dotViewer.repaint()


    def AstzoomOut(self):
        self.AstdotViewer.zoom_factor *= 0.8
        self.AstdotViewer.repaint()
    def AstzoomReset(self):
        self.AstdotViewer.zoom_factor = 1.0
        self.AstdotViewer.repaint()
    def AstzoomIn(self):
        self.AstdotViewer.zoom_factor *= 1.2
        self.AstdotViewer.repaint()

    def reload_css(self):
        style_sheet = self.load_file_content(self.QSS_FILE)
        self.ui.StyleSheet.setStyleSheet(style_sheet)

    def toggle_nav(self):
        start = self.ui.Tabbar.width()
        end = 200 if start == 45 else 45
        self.animate_width(self.ui.Tabbar, start, end)

    def toggle_examples(self):
        start = self.ui.ExamplesBar.width()
        end = 200 if start == 0 else 0
        self.animate_width(self.ui.ExamplesBar, start, end)
        if end == 200:
            self.populate_examples()

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
            self.ui.Maximize.setIcon(self.ICON_MAXIMIZE)
        else:
            self.showMaximized()
            self.ui.Maximize.setIcon(self.ICON_RESTORE)

    def animate_width(self, widget, start, end):
        self.animation = QPropertyAnimation(widget, b"minimumWidth")
        self.animation.setDuration(self.ANIMATION_DURATION)
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.setEasingCurve(self.ANIMATION_EASING_CURVE)
        self.animation.start()

    def setup_syntax_highlighting(self):
        self.CodeHighlighter = SyntaxHighlighter(self.ui.Editor.document())
        self.AssemblyHighlighter = SyntaxHighlighter(self.ui.AssemblyEditor.document())

    def setup_line_number_area(self):
        self.lineNumberAreaCodeEditor = LineNumberArea(self.ui.Editor)
        self.lineNumberAreaAssemblyEditor = LineNumberArea(self.ui.AssemblyEditor)

    def populate_examples(self):
        self.ui.ExamplesListView.clear()
        for filename in os.listdir("./examples"):
            if filename.endswith(".tripla"):
                file_item = QListWidgetItem(self.ICON_FILE_SMALL, filename)
                self.ui.ExamplesListView.addItem(file_item)
            if filename.endswith(".while"):
                file_item = QListWidgetItem(self.ICON_FILE_SMALL_ACCENT, filename)
                self.ui.ExamplesListView.addItem(file_item)

    def load_example(self, item):
        file_path = os.path.join("./examples", item.text())
        with open(file_path, 'r') as file:
            self.reset()
            content = file.read()
            self.ui.Editor.setPlainText(content)
            self.ui.AssemblyEditor.setPlainText(content)
            self.ui.Pages.setCurrentIndex(PageIndex.Code)
            self.ui.Code.setChecked(True)



            #### CONTROL
            
    def runCode(self):
        self.lineNumberAreaCodeEditor.setTargetLines([])
        ast = self.triplaYacc.parse(self.ui.Editor.toPlainText())
        mark_lines = []
        self.CodeHighlighter.clear_all_underlines()
        self.ui.Console.setPlainText("")
        for x in(self.triplaYacc.lex_errors + self.triplaYacc.yacc_errors  ):
            if not x in mark_lines:
                mark_lines += [x["lineno"]]
            if(x["lexpos"]>0):
                self.CodeHighlighter.underline_red(x["lexpos"])
        self.lineNumberAreaCodeEditor.setTargetLines(mark_lines)
        console_string = ""
        for x in(self.triplaYacc.yacc_errors):
            console_string += '<p style="color:#ff5555;">SyntaxError at line ' + str(x["lineno"]) + '</p>'
        for x in(self.merge_ranges(self.triplaYacc.lex_errors)):
            console_string += '<span style="color:#ff5555;">Illegal String "' + x["value"] + '" at line ' + str(x["lineno"]) + '</span><br>'
        if(len(self.triplaYacc.lex_errors + self.triplaYacc.yacc_errors) > 0 ):
            self.ui.Console.setHtml("<p>[ "+str(QDateTime.currentDateTime().toString("hh:mm:ss"))+" ] Building ...</p>"+console_string)
        else:
            self.ui.Console.setHtml("<p>[ "+str(QDateTime.currentDateTime().toString("hh:mm:ss"))+" ] Building ...</p>" + '<p style="color:#50fa7b">Correct Grammar</p>')
        if(len(self.triplaYacc.lex_errors + self.triplaYacc.yacc_errors) > 0):
            self.dotViewer.load_dot('digraph{ graph [bgcolor="#282a36"]; }')
            self.AstdotViewer.load_dot('digraph{ graph [bgcolor="#282a36"]; }')
            self.ui.AssemblyEditor.setPlainText("")
        else:
            parse_tree = ast.getParseTree();
            ast_tree = ast.getAstTree();
            self.dotViewer.load_dot(parse_tree.source)
            self.AstdotViewer.load_dot(ast_tree.source)
            self.ui.AssemblyEditor.setPlainText(self.ui.Editor.toPlainText())
            self.zoomReset()
            self.AstzoomReset()
    


    def merge_ranges(self, data):
        merged_ranges = []

        # Iterate through the sorted list and merge consecutive ranges
        current_range = {"lineno": None, "values": [], "lexpos": None}
        for item in data:
            if current_range["lexpos"] is None or item["lexpos"] == current_range["lexpos"] + 1:
                current_range["values"].append(item["value"])
                current_range["lexpos"] = item["lexpos"]
                current_range["lineno"] = item["lineno"]
            else:
                merged_ranges.append({
                    "lineno": current_range["lineno"],
                    "lexpos": current_range["lexpos"],
                    "value": "".join(current_range["values"])
                })
                current_range = {"lineno": item["lineno"], "values": [item["value"]], "lexpos": item["lexpos"]}

        # Add the last range
        if current_range["lexpos"] is not None:
            merged_ranges.append({
                "lineno": current_range["lineno"],
                "lexpos": current_range["lexpos"],
                "value": "".join(current_range["values"])
            })

        return merged_ranges
    
        # Add the last range
        if current_range["lineno"] is not None:
            merged_ranges.append({
                "lineno": current_range["lineno"],
                "lexpos": current_range["lexpos"],
                "value": "".join(current_range["values"])
            })

        return merged_ranges

    def reset(self):
        self.CodeHighlighter.clear_all_underlines()
        self.lineNumberAreaCodeEditor.setTargetLines([])
        self.ui.ListStack.clear()
        self.ui.ListCode.clear()

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
