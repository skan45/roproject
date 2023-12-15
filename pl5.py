import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import gurobipy as gp
from gurobipy import GRB

class AntennaPlacementSolver(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Antenna Optimizer')

        # Title label
        self.label_title = QLabel('Antenna Solver', self)
        font = self.label_title.font()
        font.setPointSize(25)
        self.label_title.setFont(font)

        # Labels and input widgets
        self.num_antennes_label = QLabel('Number of Antennas:')
        self.num_antennes_entry = QLineEdit(self)

        self.num_zones_label = QLabel('Number of Zones:')
        self.num_zones_entry = QLineEdit(self)

        self.min_antennes_label = QLabel('Minimum Antennas per Zone (comma-separated):')
        self.min_antennes_entry = QLineEdit(self)

        # Solve button
        self.solve_button = QPushButton('Résoudre', self)
        self.solve_button.setStyleSheet(
            "QPushButton { border-radius: 20px; background-color: #0577a8; color: white; font-weight: bold; font-size: 12pt; }"
            "QPushButton:hover{ border: 2px #C6C6C6 solid; color: #fff; background: #0892D0; }"
        )
        self.solve_button.clicked.connect(self.solve_antenna_optimization)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label_title)
        layout.addSpacing(10)  # Add space
        layout.addWidget(self.num_antennes_label)
        layout.addWidget(self.num_antennes_entry)
        layout.addWidget(self.num_zones_label)
        layout.addWidget(self.num_zones_entry)
        layout.addWidget(self.min_antennes_label)
        layout.addWidget(self.min_antennes_entry)
        layout.addWidget(self.solve_button)

        

    def solve_antenna_optimization(self):
        try:
            # Get user input
            num_antennes = int(self.num_antennes_entry.text())
            num_zones = int(self.num_zones_entry.text())
            min_antennes_par_zone = [int(x) for x in self.min_antennes_entry.text().split(',')]

            # Call the optimization function
            result_text = self.run_optimizer(num_antennes, num_zones, min_antennes_par_zone)

            # Display the result in a pop-up window
            self.show_result_popup(result_text)

        except Exception as e:
            # Display an error message for invalid input
            error_msg = 'Oops, an error occurred! '
            self.show_error_popup(error_msg)

    def run_optimizer(self, num_antennes, num_zones, min_antennes_par_zone):
        # Create Gurobi model
        model = gp.Model('Antenna_Optimization')

        # Decision variables
        antennas = model.addVars(num_antennes, vtype=GRB.BINARY, name="antennas")

        # Objective function - Minimize the total number of antennas
        model.setObjective(antennas.sum(), GRB.MINIMIZE)

        # Constraints
        for i in range(num_zones - 1):
            model.addConstr(antennas.sum('*') == 2, f'Antennas_Between_Zones_{i + 1}')

        for i in range(num_zones):
            model.addConstr(antennas.sum('*') >= min_antennes_par_zone[i], f'Min_Antennas_Zone_{i}')

        # Optimize the model
        model.optimize()

        # Build the result text
        if model.status == gp.GRB.OPTIMAL:
            result_text = f"Optimal solution found. Number of antennas to deploy: {int(model.ObjVal)}\n"
            for i, v in enumerate(model.getVars()):
                if v.x > 0.5:
                    result_text += f"Antenna {i + 1} is deployed.\n"
        elif model.status == gp.GRB.INFEASIBLE:
            result_text = "The model is infeasible."
        elif model.status == gp.GRB.INF_OR_UNBD:
            result_text = "The model has an infinite optimal solution or is unbounded."
        else:
            result_text = "No solution found."

        return result_text

    def show_result_popup(self, result_text):
        msg = QMessageBox()
        msg.setWindowTitle("Antenna Optimization Result")
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
    gui = AntennaPlacementSolver()
    gui.show()
    sys.exit(app.exec())

