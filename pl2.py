import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
                             QLineEdit, QLabel, QTextEdit, QVBoxLayout, QMessageBox)
from gurobipy import Model, GRB, quicksum


class ProductionOptimizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production Optimization")
        self.setGeometry(100, 100, 400, 600)
        self.initUI()

    def initUI(self):
        # Central widget and layout
        widget = QWidget(self)
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        # Grid layout for input fields
        grid = QGridLayout()
        layout.addLayout(grid)

        # Input fields
        self.inputs = {}
        labels = [
            "C (Raw Material Cost):", "Cs (Storage Cost):",
            "D1 (Month 1 Demand):", "D2 (Month 2 Demand):", 
            "D3 (Month 3 Demand):", "D4 (Month 4 Demand):",
            "Ouv (Initial Workers):", "Sal (Worker Salary):",
            "Hsup (Overtime Cost):", "R (Recruitment Cost):",
            "L (Layoff Cost):", "h (Hours per Pair):",
            "H (Working Hours):", "Hmax (Max Overtime Hours):",
            "StockInit (Initial Stock):"
        ]

        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            entry = QLineEdit()
            grid.addWidget(label, i, 0)
            grid.addWidget(entry, i, 1)
            self.inputs[label_text.split()[0]] = entry

        # Button to run optimization
        run_button = QPushButton("Run Optimization")
        run_button.clicked.connect(self.run_optimization)
        layout.addWidget(run_button)

        # Text area to display results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

    def PL2(self, months_number, raw_material_cost, storage_cost, demand, initial_workers, worker_salary, overtime_cost, recruitment_cost, layoff_cost, hours_per_pair, working_hours, max_overtime_hours, initial_stock):
        m = Model('PL2')

        # Decision Variables
        production = m.addVars(months_number, vtype=GRB.INTEGER, name="Production")
        workers = m.addVars(months_number, vtype=GRB.INTEGER, name="Workers")
        stock = m.addVars(months_number, vtype=GRB.INTEGER, lb=0, name="Stock")
        hired = m.addVars(months_number-1, vtype=GRB.INTEGER, lb=0, name="Hired")
        laid_off = m.addVars(months_number-1, vtype=GRB.INTEGER, lb=0, name="Laid_Off")
        overtime = m.addVars(months_number, vtype=GRB.INTEGER, lb=0, name="Overtime")

        # Objective Function
        m.setObjective(
            quicksum(raw_material_cost * production[m] for m in range(months_number)) +
            quicksum(storage_cost * stock[m] for m in range(months_number)) +
            quicksum(worker_salary * workers[m] for m in range(months_number)) +
            quicksum(overtime_cost * overtime[m] for m in range(months_number)) +
            quicksum(recruitment_cost * hired[m] for m in range(months_number-1)) +
            quicksum(layoff_cost * laid_off[m] for m in range(months_number-1)),
            GRB.MINIMIZE
        )

        # Constraints
        # Stock and production must meet demand
        for mu in range(months_number):
            m.addConstr(stock[mu] + production[mu] == demand[mu] + (stock[mu-1] if mu > 0 else initial_stock))

        # Workers balance
        for mi in range(1, months_number):
            m.addConstr(workers[mi] == workers[mi-1] + hired[mi-1] - laid_off[mi-1])

        # Initial number of workers
        m.addConstr(workers[0] == initial_workers)

        # Overtime per worker
        for mp in range(months_number):
            m.addConstr(overtime[mp] <= max_overtime_hours * workers[mp])

        # Production capacity
        for mo in range(months_number):
            m.addConstr(production[mo] * hours_per_pair <= working_hours * workers[mo] + overtime[mo])

        # Non-negativity of stock
        for mo in range(months_number):
            m.addConstr(stock[mo] >= 0)

        # Optimize
        m.optimize()

        # Check if the solution is optimal and return results
        results = {}
        if m.status == GRB.OPTIMAL:
            for month in range(months_number):
                results[f"Month {month+1}"] = {
                    "Production": production[month].X,
                    "Workers": workers[month].X,
                    "Stock": stock[month].X,
                    "Hired": hired[month].X if month < months_number-1 else None,
                    "Laid_Off": laid_off[month].X if month < months_number-1 else None,
                    "Overtime": overtime[month].X
                }
        else:
            raise Exception('No optimal solution found')

        return results

    def run_optimization(self):
        try:
            C = float(self.inputs['C'].text())
            Cs = float(self.inputs['Cs'].text())
            D = [float(self.inputs[f'D{i+1}'].text()) for i in range(4)]
            Ouv = int(self.inputs['Ouv'].text())
            Sal = float(self.inputs['Sal'].text())
            Hsup = float(self.inputs['Hsup'].text())
            R = float(self.inputs['R'].text())
            L = float(self.inputs['L'].text())
            h = float(self.inputs['h'].text())
            H = float(self.inputs['H'].text())
            Hmax = float(self.inputs['Hmax'].text())
            StockInit = float(self.inputs['StockInit'].text())

            results = self.PL2(
                4, C, Cs, D, Ouv, Sal, Hsup, R, L, h, H, Hmax, StockInit
            )

            # Display the results
            self.result_text.clear()
            for month, data in results.items():
                self.result_text.append(f"Results for {month}:\n")
                for key, value in data.items():
                    if value is not None:  # Only display non-None values
                        self.result_text.append(f"{key}: {value}")
                self.result_text.append("")

        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")


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
    ex = ProductionOptimizationApp()
    ex.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()
