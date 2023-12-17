import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QMessageBox)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QColor, QPen
from gurobipy import Model, GRB

def generate_random_color():
    return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class InteractiveMap(QGraphicsView):
    def __init__(self, zones, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setFixedSize(800, 600)
        self.sites = []
        self.zones = zones
        self.draw_zones()
        self.setMouseTracking(True)

    def draw_zones(self):
        boundary_pen = QPen(QColor(0, 0, 0), 10)  # Thick black border for zones
        for zone_name, zone_info in self.zones.items():
            rect = QRectF(zone_info['x'], zone_info['y'], zone_info['width'], zone_info['height'])
            zone_rect = QGraphicsRectItem(rect)
            zone_rect.setBrush(QBrush(zone_info['color']))
            zone_rect.setPen(boundary_pen)
            self.scene.addItem(zone_rect)
            self.zones[zone_name]['rect'] = zone_rect

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        on_boundary = self.is_on_boundary(scene_pos)
        if on_boundary:
            self.setCursor(Qt.CrossCursor)  # Change cursor style when on boundary
        else:
            self.setCursor(Qt.ArrowCursor)  # Default cursor elsewhere

    def is_on_boundary(self, pos):
        for zone_info in self.zones.values():
            if zone_info['rect'].sceneBoundingRect().contains(pos):
                return True
        return False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.add_site(event.pos())

    def add_site(self, pos):
        scene_pos = self.mapToScene(pos)
        if self.is_on_boundary(scene_pos):
            site = QGraphicsEllipseItem(scene_pos.x() - 5, scene_pos.y() - 5, 10, 10)
            site.setBrush(QBrush(Qt.white))  # Set site color to white
            self.scene.addItem(site)
            self.sites.append((site, None))

class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.zones = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Antenna Placement Optimization')
        main_layout = QVBoxLayout(self.central_widget)

        zone_layout = QHBoxLayout()
        self.zones_input = QLineEdit()
        self.zones_submit_button = QPushButton('Submit Zones')
        zone_layout.addWidget(QLabel('Enter zones (comma-separated):'))
        zone_layout.addWidget(self.zones_input)
        zone_layout.addWidget(self.zones_submit_button)

        main_layout.addLayout(zone_layout)

        self.zones_submit_button.clicked.connect(self.submit_zones)

        self.map_view = None
        self.solve_button = QPushButton('Solve Optimization', self)
        self.solve_button.clicked.connect(self.solve_optimization)
        self.solve_button.setEnabled(False)
        main_layout.addWidget(self.solve_button)

    def submit_zones(self):
        zones_str = self.zones_input.text()
        zone_names = [zone_name.strip() for zone_name in zones_str.split(',') if zone_name.strip()]
        num_zones = len(zone_names)
        if num_zones > 0:
            self.define_zones(num_zones, zone_names)
            self.init_map_view()
            self.solve_button.setEnabled(True)
        else:
            QMessageBox.warning(self, 'Warning', 'Please enter at least one zone.', QMessageBox.Ok)

    def define_zones(self, num_zones, zone_names):
        zone_width, zone_height = 200, 150
        for i, zone_name in enumerate(zone_names):
            x = (i % 2) * zone_width
            y = (i // 2) * zone_height
            self.zones[zone_name] = {'x': x, 'y': y, 'width': zone_width, 'height': zone_height, 'color': generate_random_color()}

    def init_map_view(self):
        if self.map_view:
            self.map_view.deleteLater()

        self.map_view = InteractiveMap(self.zones, self)
        self.central_widget.layout().addWidget(self.map_view)

    def solve_optimization(self):
        try:
            model = Model("antenna_placement")
            sites = model.addVars(len(self.map_view.sites), vtype=GRB.BINARY, name="Site")
            model.setObjective(sites.sum(), GRB.MINIMIZE)

            for zone_name, zone_info in self.zones.items():
                model.addConstr(sum(sites[i] for i, (site_item, _) in enumerate(self.map_view.sites)
                                    if zone_info['rect'].sceneBoundingRect().intersects(site_item.sceneBoundingRect())) >= 1, f"cover_{zone_name}")

            model.optimize()

            if model.status == GRB.OPTIMAL:
                for i, (site_item, _) in enumerate(self.map_view.sites):
                    if sites[i].X > 0.5:
                        site_item.setBrush(QBrush(Qt.green))
                QMessageBox.information(self, 'Optimization Result', 'Optimization completed successfully.')
            else:
                QMessageBox.warning(self, 'Optimization Result', 'No feasible solution found.')

        except Exception as e:
            QMessageBox.critical(self, 'Optimization Error', str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    stylesheet = """
    QWidget{
        background: #262D37;
    }
    QLabel{
        color: #fff;
        font-size: 12pt;
    }
    QPushButton {
        color: white;
        background: #0577a8;
        border: 2px #DADADA solid;
        padding: 10px 20px;
        font-weight: bold;
        outline: none;
    }
    QPushButton:hover{
        border: 2px #C6C6C6 solid;
        color: #fff;
        background: #0892D0;
    }
    QLineEdit {
        padding: 5px;
        color: #fff;
        border-style: solid;
        border: 2px solid #fff;
        border-radius: 8px;
        font-size: 12pt;
    }
    """
    app.setStyleSheet(stylesheet)
    main_window = MainApplicationWindow()
    main_window.show()
    sys.exit(app.exec_())
