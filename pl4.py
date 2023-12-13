import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox
import gurobipy as gp
from gurobipy import GRB

# Given data from the problem statement
populations = [2, 3, 4, 5, 6, 7, 8, 9, 10]  # Population in millions
adjacency_matrix = [
    # Adjacency matrix provided in the problem statement
    [1, 1, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 1],
    [0, 0, 0, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 0, 1, 1],
]


# Optimization model class
class BankBranchOptimization:
    def __init__(self, populations, adjacency_matrix, budget, branch_cost, dab_cost, a_coverage, b_coverage,
                 c_coverage):
        self.populations = populations
        self.adjacency_matrix = adjacency_matrix
        self.budget = budget
        self.branch_cost = branch_cost
        self.dab_cost = dab_cost
        self.a_coverage = a_coverage
        self.b_coverage = b_coverage
        self.c_coverage = c_coverage

    def run(self):
        model = gp.Model("BankBranchOptimization")

        # Decision variables
        branches = model.addVars(len(self.populations), vtype=GRB.BINARY, name="branches")
        dabs = model.addVars(len(self.populations), vtype=GRB.BINARY, name="dabs")

        # Objective function: Maximize population coverage
        model.setObjective(
            gp.quicksum(self.populations[i] * (self.a_coverage * branches[i] +
                                               self.b_coverage * dabs[i] +
                                               self.c_coverage * (1 - branches[i]) * (1 - dabs[i]))
                        for i in range(len(self.populations))), GRB.MAXIMIZE)

        # Budget constraint
        model.addConstr(self.branch_cost * gp.quicksum(branches[i] for i in range(len(self.populations))) +
                        self.dab_cost * gp.quicksum(dabs[i] for i in range(len(self.populations))) <= self.budget,
                        "Budget")

        # Neighboring regions constraint
        for i in range(len(self.adjacency_matrix)):
            for j in range(i + 1, len(self.adjacency_matrix[i])):
                if self.adjacency_matrix[i][j] == 1:
                    model.addConstr(branches[i] + branches[j] <= 1, f"Neighboring_{i}_{j}")

        # Solve the model
        model.optimize()

        # Collect results
        branches_solution = model.getAttr('x', branches)
        dabs_solution = model.getAttr('x', dabs)
        return branches_solution, dabs_solution


# GUI class
class BankBranchOptimizationGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Bank Branch Optimization GUI")

        # Create input widgets
        self.budget_entry = QLineEdit(self)
        self.branch_cost_entry = QLineEdit(self)
        self.dab_cost_entry = QLineEdit(self)
        self.a_coverage_entry = QLineEdit(self)
        self.b_coverage_entry = QLineEdit(self)
        self.c_coverage_entry = QLineEdit(self)

        # Add labels and entries to layout
        input_layout = QVBoxLayout()
        labels_entries = {
            "Total Budget (B)": self.budget_entry,
            "Branch Cost (K)": self.branch_cost_entry,
            "DAB Server Cost (D)": self.dab_cost_entry,
            "A Coverage (a)": self.a_coverage_entry,
            "B Coverage (b)": self.b_coverage_entry,
            "C Coverage (c)": self.c_coverage_entry
        }

        for label, entry in labels_entries.items():
            label_widget = QLabel(label, self)
            input_layout.addWidget(label_widget)
            input_layout.addWidget(entry)

        # Add run button
        run_button = QPushButton("Run Optimization", self)
        run_button.clicked.connect(self.run_gui_optimization)

        # Add text widget to display results
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(run_button)
        main_layout.addWidget(self.result_text)

        self.setGeometry(100, 100, 420, 450)

    def run_gui_optimization(self):
        try:
            # Get values from entries
            budget = float(self.budget_entry.text())
            branch_cost = float(self.branch_cost_entry.text())
            dab_cost = float(self.dab_cost_entry.text())
            a_coverage = float(self.a_coverage_entry.text()) / 100  # Convert percentage to proportion
            b_coverage = float(self.b_coverage_entry.text()) / 100  # Convert percentage to proportion
            c_coverage = float(self.c_coverage_entry.text()) / 100  # Convert percentage to proportion

            # Create an instance of the optimization model
            optimization_model = BankBranchOptimization(populations, adjacency_matrix, budget, branch_cost, dab_cost,
                                                        a_coverage, b_coverage, c_coverage)

            # Run the optimization
            branches_solution, dabs_solution = optimization_model.run()

            # Display results
            self.result_text.clear()  # Clear previous results
            self.result_text.insertPlainText("Optimal solution:\n")
            for i in range(len(populations)):
                branch_status = 'Yes' if branches_solution[i] > 0.5 else 'No'
                dab_status = 'Yes' if dabs_solution[i] > 0.5 else 'No'
                self.result_text.insertPlainText(f"Region {i + 1} - Branch: {branch_status}, DAB: {dab_status}\n")

        except gp.GurobiError as e:
            QMessageBox.critical(self, "Gurobi Error", str(e))
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please ensure all inputs are numbers.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


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
    gui = BankBranchOptimizationGUI()
    gui.show()
    sys.exit(app.exec_())

