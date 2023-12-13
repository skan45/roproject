import sys
from gurobipy import Model, GRB, quicksum
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QGridLayout, QPushButton, QLineEdit, QLabel,QMessageBox)

class AgriculturalZoneOptimizationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the main window's properties
        self.setWindowTitle('Agricultural Zone Optimization')
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.gridLayout = QGridLayout(self.centralWidget)

        # Parameters and cultures
        self.params = ['yield', 'price', 'labor', 'machine_time', 'water', 'labor_cost', 'fixed_cost']
        self.cultures = ['Blé', 'Orge', 'Mais', 'Bet-sucr', 'Tournesol']
        self.entries = {}
        self.additional_entries = {}
        self.default_values = {
            'Blé': {'yield': 75, 'price': 60, 'labor': 2, 'machine_time': 30, 'water': 3000, 'labor_cost': 500, 'fixed_cost': 250},
            'Orge': {'yield': 60, 'price': 50, 'labor': 1, 'machine_time': 24, 'water': 2000, 'labor_cost': 500, 'fixed_cost': 180},
            'Mais': {'yield': 55, 'price': 66, 'labor': 2, 'machine_time': 20, 'water': 2500, 'labor_cost': 600, 'fixed_cost': 190},
            'Bet-sucr': {'yield': 50, 'price': 110, 'labor': 3, 'machine_time': 28, 'water': 3800, 'labor_cost': 700, 'fixed_cost': 310},
            'Tournesol': {'yield': 60, 'price': 60, 'labor': 2, 'machine_time': 25, 'water': 3200, 'labor_cost': 550, 'fixed_cost': 320}
        }
        self.additional_defaults = {
            'Irrigation water (m3)': "25000000",
            'Machine hours': "24000",
            'Labor': "3000"
        }

        # Create input fields for each parameter and culture
        for i, param in enumerate(self.params):
            for j, cult in enumerate(self.cultures):
                # Add label for the culture if it's the first parameter row
                if i == 0:
                    label = QLabel(cult)
                    self.gridLayout.addWidget(label, i, j+1)

                # Add label for the parameter
                label = QLabel(param)
                self.gridLayout.addWidget(label, i+1, 0)

                # Create a line edit for each parameter for each culture
                line_edit = QLineEdit()
                self.gridLayout.addWidget(line_edit, i+1, j+1)
                self.entries.setdefault(cult, {})[param] = line_edit

        # Additional inputs for global constraints
        self.additional_labels = ['Irrigation water (m3)', 'Machine hours', 'Labor']
        
        for i, label_text in enumerate(self.additional_labels, len(self.params) + 2):
            label = QLabel(label_text)
            line_edit = QLineEdit()
            self.gridLayout.addWidget(label, i, 0)
            self.gridLayout.addWidget(line_edit, i, 1)
            self.additional_entries[label_text] = line_edit
        for cult, params in self.default_values.items():
            for param, value in params.items():
                line_edit = QLineEdit(str(value))
                self.gridLayout.addWidget(line_edit, self.params.index(param)+1, self.cultures.index(cult)+1)
                self.entries.setdefault(cult, {})[param] = line_edit

        # Set default values for additional entries
        for i, (label_text, default) in enumerate(self.additional_defaults.items(), len(self.params) + 2):
            line_edit = QLineEdit(default)
            self.gridLayout.addWidget(line_edit, i, 1)
            self.additional_entries[label_text] = line_edit    
        # Solve button (doesn't do anything yet)
        self.solveButton = QPushButton('Solve LP')
        ###self.solveButton.clicked.connect(self.solve_agriculture_probelm)
        self.gridLayout.addWidget(self.solveButton, len(self.params) + len(self.additional_labels) + 3, 0, 1, len(self.cultures) + 1)
        self.solveButton.clicked.connect(self.solve_agriculture_problem)

    # Placeholder for the solveLP function
    def solve_agriculture_problem(self):
        try:
            # Check for negative values in the main entries
            for cult, params in self.entries.items():
                for param, line_edit in params.items():
                    value = float(line_edit.text())
                    if value < 0:
                        raise ValueError(f"Value for {param} in {cult} cannot be negative.")

            # Check for negative values in the additional entries
            for label_text, line_edit in self.additional_entries.items():
                value = float(line_edit.text())
                if value < 0:
                    raise ValueError(f"Value for {label_text} cannot be negative.")

            # Call the solver function if inputs are valid
            result_text = self.run_solver()
            # Display the result in a pop-up window
            self.show_result_popup(result_text)

        except ValueError as e:
            self.show_error_popup(str(e))
        except Exception as e:
            self.show_error_popup(f"An unexpected error occurred: {e}")

    def run_solver(self):
        # Retrieve values from the entries
        values = {cult: {param: float(self.entries[cult][param].text()) for param in self.params} for cult in self.cultures}
        irrigation_water = float(self.additional_entries['Irrigation water (m3)'].text())
        machine_hours = float(self.additional_entries['Machine hours'].text())
        labor = float(self.additional_entries['Labor'].text())

        # Create a new model
        m = Model("agriculture")

        # Create variables
        x = m.addVars(self.cultures, name="cultures")

        # Set the objective
        m.setObjective(
            quicksum(
                x[cult] * (values[cult]['yield'] * values[cult]['price'] -
                           values[cult]['labor'] * values[cult]['labor_cost'] -
                           values[cult]['machine_time'] * 30 -
                           values[cult]['water'] * 0.1 - values[cult]['fixed_cost'])
                for cult in self.cultures), GRB.MAXIMIZE)

        # Add constraints
        m.addConstr(quicksum(x[cult] * values[cult]['labor'] for cult in self.cultures) <= labor, "Labor")
        m.addConstr(quicksum(x[cult] * values[cult]['machine_time'] for cult in self.cultures) <= machine_hours, "MachineHours")
        m.addConstr(quicksum(x[cult] * values[cult]['water'] for cult in self.cultures) <= irrigation_water, "IrrigationWater")

        # Optimize model
        m.optimize()

        # Display results
        result = "\n".join(f"{cult} hectares: {x[cult].X}" for cult in self.cultures)
        result += f"\nOptimal profit: {m.objVal}"
        return result

    def show_result_popup(self, result_text):
        msg = QMessageBox()
        msg.setWindowTitle("Agriculture Result")
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
       

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
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
    """)
    ex = AgriculturalZoneOptimizationUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
