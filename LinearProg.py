from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from pl3 import PL3_Ui
from pl5 import MainApplicationWindow
from pl6 import AddNetworkElements,Networkproblem
from pl1 import AgriculturalZoneOptimizationUI
from pl2 import ProductionOptimizationApp
from pl4 import BankBranchOptimizationGUI
import sys

class LPInterface(QWidget):
    def __init__(self):
        super(LPInterface, self).__init__()
        self.setWindowTitle("Linear Programming Interface")
        self.setFixedSize(600, 400)

        label = QLabel("Linear Programming Problems")
        label.setAlignment(Qt.AlignCenter)

        button1 = QPushButton("Exercice 1")
        button2 = QPushButton("Exercice 2")
        button3 = QPushButton("Exercice 3")
        button4 = QPushButton("Exercice 4")
        button5 = QPushButton("Exercice 5")
        button6 = QPushButton("Exercice 6")
        button1.clicked.connect(self.show_pl1_ui)
        button2.clicked.connect(self.show_pl2_ui) 
        button3.clicked.connect(self.show_pl3_ui)
        button4.clicked.connect(self.show_pl4_ui)
        button5.clicked.connect(self.show_pl5_ui)
        button6.clicked.connect(self.show_pl6_ui)
        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(label, alignment=Qt.AlignCenter)
        # Create horizontal layouts for left and right buttons
        left_button_layout = QHBoxLayout()
        left_button_layout.addWidget(button1)
        left_button_layout.addWidget(button2)
        left_button_layout.addWidget(button3)

        right_button_layout = QHBoxLayout()
        right_button_layout.addWidget(button4)
        right_button_layout.addWidget(button5)
        right_button_layout.addWidget(button6)

        # Add the left and right button layouts to the main layout
        layout.addLayout(left_button_layout)
        layout.addLayout(right_button_layout)

        # Set main layout for the window
        self.setLayout(layout)
        self.pl1_ui=AgriculturalZoneOptimizationUI()
        self.pl2_ui=ProductionOptimizationApp()
        self.pl3_ui = PL3_Ui()
        self.pl4_ui = BankBranchOptimizationGUI()
        self.pl5_ui = MainApplicationWindow()
        self.pl6_ui= AddNetworkElements(Networkproblem())

    def show_pl3_ui(self):
        self.pl3_ui.show()
    def show_pl4_ui(self):
        self.pl4_ui.show()    
    def show_pl1_ui(self):
        self.pl1_ui.show()
    def show_pl2_ui(self):
        self.pl2_ui.show()        
    def show_pl5_ui(self):
        self.pl5_ui.show()
    def show_pl6_ui(self):
        self.pl6_ui.show()    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    style = """
        QWidget{
            background: #262D37;
            margin: "auto";
        }
        QLabel{
            color: #fff;
            font-size: 20pt;
        }
        QPushButton {
            color: white;
            background: #0577a8;
            border: 2px #DADADA solid;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 8px;
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
    app.setStyleSheet(style)
    window = LPInterface()
    window.show()
    sys.exit(app.exec())
