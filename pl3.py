import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import numpy as np
import gurobipy as gp
from gurobipy import quicksum
import pandas as pd

class PL3_Ui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('PL3 : Répartition des Employés')
        self.createLayout()
       

    def createLayout(self):
        layout = QtWidgets.QVBoxLayout()
        # Title and Problem Description
        title_label = QtWidgets.QLabel('Répartition des Employés')
        title_label.setStyleSheet("color: #fff; font-size: 16pt; font-weight: bold;")

        description_label = QtWidgets.QLabel(
            "Entrez le nombre d'employés nécessaires pour chaque jour. L'objectif est de minimiser le nombre total d'employés tout en respectant les exigences minimales pour chaque jour."
        )
        description_label.setStyleSheet("color: #fff; font-size: 12pt;")
        description_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addSpacing(20)  # Add space

        # Day Labels and Input Fields
        self.labels = [
            "Nombre d'employés Pour Lundi", "Nombre d'employés Pour Mardi", "Nombre d'employés Pour Mercredi",
            "Nombre d'employés Pour Jeudi", "Nombre d'employés Pour Vendredi", "Nombre d'employés Pour Samedi",
            "Nombre d'employés Pour Dimanche"
        ]
        self.input_fields = []

        for label in self.labels:
            label_widget = QtWidgets.QLabel(label)
            input_field = QtWidgets.QLineEdit()
            self.input_fields.append(input_field)

            # Set style for label
            label_widget.setStyleSheet("color: #fff; font-size: 12pt;")

            # Set style for input field
            input_field.setStyleSheet(
                "padding: 5px; color: #fff; border-style: solid; border: 2px solid #fff; border-radius: 8px; font-size: 12pt;"
            )

            layout.addWidget(label_widget)
            layout.addWidget(input_field)

        # Results Button
        results_button = QtWidgets.QPushButton('Résoudre')
        results_button.clicked.connect(self.planification)
        results_button.setStyleSheet(
            "QPushButton { border-radius: 20px; background-color: #0577a8; color: white; font-weight: bold; font-size: 12pt; }"
            "QPushButton:hover{ border: 2px #C6C6C6 solid; color: #fff; background: #0892D0; }"
        )

        layout.addWidget(results_button)

        self.setLayout(layout)

    def planification(self):
        try:
            # ===================INITILISATION
            x1, x2, x3, x4, x5, x6, x7 = [int(field.text()) for field in self.input_fields]
            jours = [x1, x2, x3, x4, x5, x6, x7]
            jour = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            mat = np.ones((7, 7), dtype=int)
            for c in range(7):
                i = c + 5
                mat[i % 7, c] = 0
                mat[(i + 1) % 7, c] = 0

            # ===================MODEL
            PL3 = gp.Model("PL3")
            x = []
            for i in range(7):
                x.append(PL3.addVar(lb=0, vtype=gp.GRB.INTEGER, name='x' + str(i + 1)))
            X = np.array(x)
            X = X.reshape((1, 7))
            for j in range(7):
                PL3.addConstr(gp.quicksum(mat[j, :] * x) >= jours[j],
                            "Nbre d'employé min requis pour " + jour[j] + " est " + str(jours[j]))

            PL3.setObjective(gp.quicksum(x), gp.GRB.MINIMIZE)

            PL3.optimize()

            # ===================PLANIFICATION
            aux = []
            for i in range(7):
                aux.append(int(x[i].x))
            result = []
            for i in range(7):
                result.append(aux[(i + 2) % 7])
            with open("Resolutions/PL3.txt", "w") as f:
                sys.stdout = f
                sheet = {}
                print("plannification des congés ")
                for i in range(7):
                    print(jour[i] + "  :" + str(result[i]))
                    sheet.update({jour[i]: [result[i]]})
                df = pd.DataFrame(sheet)
                df.to_excel("Resolution_excel/pl3.xlsx", index=False)

                # ===================RESOLUTION
                print("le nombre totale optimale des employés est ", int(PL3.objVal))
                # ===================DISPLAY RESULTS
                result_text = "Plannification des congés :\n"
                for i in range(7):
                    result_text += f"{jour[i]}  : {result[i]}\n"

                result_text += f"Le nombre total optimal des employés est {int(PL3.objVal)}" if hasattr(PL3, 'objVal') else \
                    "Le nombre total optimal des employés n'est pas défini."

                # Display results in a pop-up window
                self.show_results_popup(result_text)
        except Exception as e:
            # Show error message in a pop-up window
            error_msg = f"An error occurred !!"
            self.show_error_popup(error_msg)

    def show_results_popup(self, result_text):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Résultats de la planification")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(result_text)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()
    
    def show_error_popup(self, error_msg):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Error")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(error_msg)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
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
    window = PL3_Ui()
    window.show()
    sys.exit(app.exec())

