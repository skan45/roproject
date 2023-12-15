import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import gurobipy as gp
from gurobipy import quicksum
import matplotlib.pyplot as plt
import networkx as nx

class AddNetworkElements(QWidget):
    def __init__(self, network_problem_instance):
        super().__init__()
        self.network_problem_instance = network_problem_instance
        self.network_problem_instance.add_network_elements = self  
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Add Network Elements')

        layout = QVBoxLayout()
        router_label = QLabel('Add Router (e.g., H):')
        self.router_entry = QLineEdit(self)
        add_router_button = QPushButton('Add Router', self)
        add_router_button.clicked.connect(self.add_router)
        edge_label = QLabel('Add Edge (Format: A,B,Weight e.g., A,H,5):')
        self.edge_entry = QLineEdit(self)
        add_edge_button = QPushButton('Add Edge', self)
        add_edge_button.clicked.connect(self.add_edge)

        # Continue button
        continue_button = QPushButton('Continue', self)
        continue_button.clicked.connect(self.close_and_continue)

        # Add widgets to layout
        layout.addWidget(router_label)
        layout.addWidget(self.router_entry)
        layout.addWidget(add_router_button)
        layout.addWidget(edge_label)
        layout.addWidget(self.edge_entry)
        layout.addWidget(add_edge_button)
        layout.addWidget(continue_button)

        self.setLayout(layout)

    def add_router(self):
        router = self.router_entry.text().strip().upper()
        if router and router not in self.network_problem_instance.routers:
            self.network_problem_instance.routers.append(router)
            msg=f"Success Router '{router}' added successfully."
            self.show_result_popup(msg)
            self.router_entry.clear()
        else:
            error= "Warning Invalid router name or router already exists."
            self.show_error_popup(error)

    def add_edge(self):
        edge_info = self.edge_entry.text().split(',')
        if len(edge_info) == 3:
            src, dest, weight = edge_info
            src, dest = src.strip().upper(), dest.strip().upper()
            try:
                weight = int(weight)
                if src in self.network_problem_instance.routers and dest in self.network_problem_instance.routers:
                    self.network_problem_instance.edges[(src, dest)] = weight
                    msg= f"Success Edge '{src}-{dest}' with weight {weight} added successfully."
                    self.show_result_popup(msg)
                    self.edge_entry.clear()
                else:
                      error="Warning One or both routers do not exist."
                      self.show_error_popup(error)
            except ValueError:
                 error="Warning Invalid weight entered. Please enter an integer."
                 self.show_error_popup(error)
        else:
            erro="Warning Invalid edge format. Please follow the format 'A,B,Weight'."
            self.show_error_popup(error)
    def close_and_continue(self):
        self.network_problem_instance.initUI()
        self.network_problem_instance.show()
        self.close()
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

class Networkproblem(QWidget):
    def __init__(self):
        super().__init__()
        self.routers = []
        self.edges = {
        }
        self.add_network_elements = None

    def initUI(self):
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Network Problem Solver')

        layout = QVBoxLayout()

        self.label_title = QLabel('Network Problem Solver', self)
        font = self.label_title.font()
        font.setPointSize(20)
        self.label_title.setFont(font)

        # Source input
        src_label = QLabel('Source name:')
        self.src_entry = QLineEdit(self)

        # Destination input
        dest_label = QLabel('Destination name:')
        self.dest_entry = QLineEdit(self)

        # Solve button
        solve_button = QPushButton('Solve Network Path', self)
        solve_button.clicked.connect(self.solve_network_path)
        back_button = QPushButton('back adding network elements', self)
        back_button.clicked.connect(self.go_back)

        # Add widgets to layout
        layout.addWidget(self.label_title)
        layout.addWidget(src_label)
        layout.addWidget(self.src_entry)
        layout.addWidget(dest_label)
        layout.addWidget(self.dest_entry)
        layout.addWidget(solve_button)
        layout.addWidget(back_button)  
        self.setLayout(layout)
    def go_back(self):
        self.hide()  # Hide the current window
        if self.add_network_elements:
            self.add_network_elements.show()    
    
    # Replace this method with your logic for solving the network problem
    def solve_network_path(self):
        try:
            #get the input from the input widget
            src=self.src_entry.text()
            dest=self.dest_entry.text()
            if src  not in self.routers and dest  not in self.routers :
               raise ValueError("Please enter the proper routers in the routers list ")
            result_text=self.run_network_solver(src,dest)
            self.show_result_popup(result_text)
        except ValueError as e:
            # Display an error message for invalid input
            error_msg = ' Please enter the proper routers in the routers list !'
            self.show_error_popup(error_msg)
        except gp.GurobiError as e:
            # Display Gurobi errors in a pop-up window
            self.show_error_popup(' Oups an Error Occured !') 
    def run_network_solver(self,src,dest):
        m = gp.Model("network_solver")
        ##variables de decision 
        vars = m.addVars(self.edges.keys(), obj=self.edges, vtype=gp.GRB.BINARY, name='e')
        for node in set(sum([list(edge) for edge in self.edges.keys()], [])):
            if node not in [src, dest]:  # Ignore source and sink for flow conservation
                m.addConstr(quicksum(vars[i, j] for i, j in self.edges.keys() if j == node) ==
                    quicksum(vars[i, j] for i, j in self.edges.keys() if i == node), name=f'node_{node}_conservation')
        m.addConstr(quicksum(vars[src, j] for i, j in self.edges.keys() if i == src) == 1, name='source_out')
        m.addConstr(quicksum(vars[i, dest] for i, j in self.edges.keys() if j == dest) == 1, name='sink_in') 
        m.optimize()
        ##retrieve solution
        if m.status == gp.GRB.OPTIMAL:
          solution_edges = [e for e in vars.keys() if vars[e].x > 0.5]
          self.draw_graph(solution_edges)
          total_time = sum(self.edges[e] for e in solution_edges)
          result_text=f"The shortest path from {src} to {dest} is: {solution_edges} with total travel time: {total_time}"
          return result_text
    def draw_graph(self, solution_edges):
        G = nx.Graph()
        G.add_nodes_from(self.routers)
        G.add_weighted_edges_from([(src, dest, self.edges[(src, dest)]) for src, dest in self.edges])
        pos = nx.spring_layout(G)  
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, edgelist=self.edges.keys(), alpha=0.3)
        nx.draw_networkx_edges(G, pos, edgelist=solution_edges, edge_color='r', width=2)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.axis('off')
        plt.show()      
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
    network_problem = Networkproblem()
    add_network_elements = AddNetworkElements(network_problem)
    add_network_elements.show()
    sys.exit(app.exec_())
