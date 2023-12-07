import graphviz
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QTransform, QColor
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

class DotViewer(QGraphicsView):
    def __init__(self):
        super(DotViewer, self).__init__()

        self.zoom_factor = 1.0
        self.pan_start_pos = None

        self.svg_widget = QSvgWidget()
        self.svg_widget.setStyleSheet("background-color: #282a36;")

        self.scene = QGraphicsScene(self)
        self.scene.addWidget(self.svg_widget)

        self.setScene(self.scene)
        self.setSceneRect(self.scene.itemsBoundingRect())


    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor

        self.zoom_factor *= factor
        self.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))

    def mousePressEvent(self, event):
        self.pan_start_pos = event.position()
        
    def mouseMoveEvent(self, event):
        if self.pan_start_pos is not None:
            pan_distance = event.position() - self.pan_start_pos

            self.pan_start_pos = event.position()

            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - pan_distance.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - pan_distance.y())

    def repaint(self):
        self.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))


    def mouseReleaseEvent(self, event):
        self.pan_start_pos = None

    def load_dot(self, dot_source):
        self.dot_source = dot_source

    
        graph = graphviz.Source(self.dot_source, format='svg')
        svg_string = graph.pipe(format='svg').decode('utf-8')
        
        # Create a QSvgWidget and load the modified SVG content
        self.svg_widget = QSvgWidget()
        self.svg_widget.load(QByteArray(svg_string.encode('utf-8')))

        # Create a QGraphicsScene and add the QSvgWidget to it
        scene = QGraphicsScene(self)
        scene.addWidget(self.svg_widget)

        # Set the scene and some properties for the view
        self.setScene(scene)
        self.setSceneRect(scene.itemsBoundingRect())
 
