import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import gurobipy as gp
from gurobipy import GRB

class AntennaPlacementSolver(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('PL5 : Antenna Placement Solver')

        # Title label
        self.label_title = QLabel('Antenna Solver', self)
        font = self.label_title.font()
        font.setPointSize(25)
        self.label_title.setFont(font)

        # Problem explanation
        explanation_label = QLabel("Entrez le nombre de zones. Les antennes ne peuvent être situées qu'entre deux zones différentes. Essayons de minimiser le nombre d'antennes nécessaires !")
        explanation_label.setWordWrap(True)

        # Input widgets
        self.num_zones_label = QLabel('Number of Zones:')
        self.num_zones_entry = QLineEdit(self)

        # Solve button
        self.solve_button = QPushButton('Resoudre', self)
        self.solve_button.setStyleSheet(
            "QPushButton { border-radius: 20px; background-color: #0577a8; color: white; font-weight: bold; font-size: 12pt; }"
            "QPushButton:hover{ border: 2px #C6C6C6 solid; color: #fff; background: #0892D0; }"
        )
        self.solve_button.clicked.connect(self.solve_antenna_placement)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label_title)
        layout.addWidget(explanation_label)
        layout.addSpacing(20)  # Add space
        layout.addWidget(self.num_zones_label)
        layout.addWidget(self.num_zones_entry)
        layout.addSpacing(20)  # Add space
        layout.addWidget(self.solve_button)
        layout.addSpacing(20)  # Add space

        # Set a minimum size for the window
        self.setMinimumSize(400, 200)

        

    def solve_antenna_placement(self):
        try:
            # Get the number of zones from the input widget
            num_zones = int(self.num_zones_entry.text())

            # Check if the entered number is positive
            if num_zones <= 0:
                raise ValueError("Please enter a positive number of zones.")

            # Call the solve_antenna_placement function
            result_text = self.run_solver(num_zones)

            # Display the result in a pop-up window
            self.show_result_popup(result_text)

        except ValueError as e:
            # Display an error message for invalid input
            error_msg = ' Oups an Error Occured !'
            self.show_error_popup(error_msg)
        except gp.GurobiError as e:
            # Display Gurobi errors in a pop-up window
            self.show_error_popup(' Oups an Error Occured !')

    def run_solver(self, num_zones):
        # Create Gurobi model
        model = gp.Model('Antenna_Placement')

        # Sites
        sites = [chr(ord('A') + i) for i in range(num_zones)]

        # Decision variables
        antennas = model.addVars(sites, vtype=GRB.BINARY, name='antennas')

        # Objective function - Minimize the total number of antennas
        model.setObjective(antennas.sum(), GRB.MINIMIZE)

        # Constraints
        for i in range(len(sites) - 1):
            model.addConstr(antennas[sites[i]] + antennas[sites[i + 1]] >= 1,
                            f'Antennas_Coverage_{sites[i]}_{sites[i + 1]}')

        # Optimize the model
        model.optimize()

        # Build the result text
        if num_zones % 2 == 1:
            result = int(model.ObjVal) + 1
        else:
            result = int(model.ObjVal)
        result_text = f"Nombre total d'antennes: {result}\n"

        return result_text

    def show_result_popup(self, result_text):
        msg = QMessageBox()
        msg.setWindowTitle("Antenna Placement Result")
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
    solver_gui = AntennaPlacementSolver()
    solver_gui.show()
    sys.exit(app.exec())
