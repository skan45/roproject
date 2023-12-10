import gurobipy as gp
from gurobipy import GRB

def solve_antenna_placement(num_sites):
    # Création du modèle Gurobi
    model = gp.Model('Antenna_Placement')

    # Sites
    sites = [chr(ord('A') + i) for i in range(num_sites)]  # Use ASCII values to generate letters

    # Variables de décision
    antennas = model.addVars(sites, vtype=GRB.BINARY, name='antennas')

    # Fonction objective - Minimiser le nombre total d'antennes
    model.setObjective(antennas.sum(), GRB.MINIMIZE)

    # Contraintes
    for i in range(len(sites) - 1):
        model.addConstr(antennas[sites[i]] + antennas[sites[i + 1]] >= 1, f'Antennas_Coverage_{sites[i]}_{sites[i + 1]}')

    # Résolution du modèle
    model.optimize()

    # Affichage des résultats
    print("Status:", model.status)
    print("Nombre total d'antennes:", int(model.ObjVal))  # Modifié objVal en ObjVal

    # Affichage de l'affectation des antennes
    for site in sites:
        print(f"{site}: {int(antennas[site].x)}")

# Example: Call the function with the desired number of sites
solve_antenna_placement(6)  # This will generate sites A, B, C, D, E, F, G







