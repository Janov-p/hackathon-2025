import sys
import os
# Ajouter le chemin racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__ ), '../', 'Utilities')))

import prevision as pv
from Utilities import jsonLoader as jl
import extractMeasure as em



dt = jl.simplification("db/chiffre_cles.json","Visites Totales")
print("#####################################")
# Méthode simple
previsione = pv.faire_prevision(dt, modele='auto')
print(previsione)

# Comparaison complète
comparaison, details = pv.comparer_modeles(dt)
print("\nComparaison :")
print(comparaison)