import sys 
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import numpy as np
import gurobipy as gp
from gurobipy import quicksum
import pandas as pd
class Networkproblem(QWidget):
    def __init__(self):
        super().__init__()
        self.userint()
    def userint(self):
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('PL6: Network problem ')
        # Title label
        self.label_title = QLabel('Network problem solver', self)
        font = self.label_title.font()
        font.setPointSize(25)
        self.label_title.setFont(font)
        # Problem explanation
        explanation_label = QLabel("Entrez la destination et le source. il faut qu'il soient differentes.")
        explanation_label.setWordWrap(True)

        # Input widgets
        self.src_label = QLabel('nom de source:')
        self.src_entry = QLineEdit(self)
        self.dest_label = QLabel('nom de destination:')
        self.dest_entry = QLineEdit(self)
        # Solve button
        self.solve_button = QPushButton('Resoudre', self)
        self.solve_button.setStyleSheet(
            "QPushButton { border-radius: 20px; background-color: #0577a8; color: white; font-weight: bold; font-size: 12pt; }"
            "QPushButton:hover{ border: 2px #C6C6C6 solid; color: #fff; background: #0892D0; }"
        )
        self.solve_button.clicked.connect(self.solve_network_path)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label_title)
        layout.addWidget(explanation_label)
        layout.addSpacing(20)  # Add space
        layout.addWidget(self.src_label)
        layout.addWidget(self.src_entry)
        layout.addSpacing(20)  # Add space
        layout.addWidget(self.dest_label)
        layout.addWidget(self.dest_entry)
        layout.addSpacing(20)  # Add space
        layout.addWidget(self.solve_button)
        layout.addSpacing(20)  # Add space
        # Set a minimum size for the window
        self.setMinimumSize(400, 200)
    
    
    def solve_network_path(self):
        routers={'A', 'B', 'C', 'D', 'E', 'F', 'G'}
        try:
            #get the input from the input widget
            src=self.src_entry.text()
            dest=self.dest_entry.text()
            if src  not in routers and dest  not in routers :
               raise ValueError("Please enter the proper routers in the routers list ")
            result_text=self.run_network_solver(src,dest)
            self.show_result_popup(result_text)
        except ValueError as e:
            # Display an error message for invalid input
            error_msg = ' Oups an Error Occured !'
            self.show_error_popup(error_msg)
        except gp.GurobiError as e:
            # Display Gurobi errors in a pop-up window
            self.show_error_popup(' Oups an Error Occured !')    
    def run_network_solver(self,src,dest):
        edges = {
    ('A', 'B'): 4,
    ('A', 'C'): 3,
    ('B', 'D'): 6,
    ('B', 'E'): 5,
    ('C', 'B'): 3,
    ('C', 'E'): 4,
    ('C', 'F'): 6,
    ('D','G'):1,
    ('D', 'E'): 2,
    ('E', 'G'): 3,
    ('F', 'E'): 4
}
        m = gp.Model("network_solver")
        ##variables de decision 
        vars = m.addVars(edges.keys(), obj=edges, vtype=gp.GRB.BINARY, name='e')
        for node in set(sum([list(edge) for edge in edges.keys()], [])):
            if node not in [src, dest]:  # Ignore source and sink for flow conservation
                m.addConstr(quicksum(vars[i, j] for i, j in edges.keys() if j == node) ==
                    quicksum(vars[i, j] for i, j in edges.keys() if i == node), name=f'node_{node}_conservation')
        m.addConstr(quicksum(vars[src, j] for i, j in edges.keys() if i == src) == 1, name='source_out')
        m.addConstr(quicksum(vars[i, dest] for i, j in edges.keys() if j == dest) == 1, name='sink_in') 
        m.optimize()
        ##retrieve solution
        if m.status == gp.GRB.OPTIMAL:
          solution_edges = [e for e in vars.keys() if vars[e].x > 0.5]
          total_time = sum(edges[e] for e in solution_edges)
          result_text=f"The shortest path from {src} to {dest} is: {solution_edges} with total travel time: {total_time}"
          return result_text
    def show_result_popup(self, result_text):
        msg = QMessageBox()
        msg.setWindowTitle("Network problem result")
        msg.setIcon(QMessageBox.Information)
        msg.setText(result_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    def show_error_popup(self, error_msg):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(error_msg)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    style = """
        QWidget{
            background: #262D37;
            margin: "auto";
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
    app.setStyleSheet(style)
    solver_gui = Networkproblem()
    solver_gui.show()
    sys.exit(app.exec())
       

        
           