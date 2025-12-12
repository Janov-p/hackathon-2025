import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

def modelAR1_ameliore(data:dict, modele='auto', saisonnalite=True):
    """
    Fonction améliorée avec plusieurs options de modélisation
    
    Paramètres:
    -----------
    data : dict
        Dictionnaire des données temporelles
    modele : str
        'auto' - sélection automatique
        'ar1' - modèle AR(1) original
        'arima' - ARIMA automatique
        'sarima' - SARIMA avec saisonnalité
    saisonnalite : bool
        Inclure la saisonnalité (True par défaut)
    """
    
    # Extraction des données
    valeurs = np.array(list(data.values()), dtype=float)
    mois = list(data.keys())
    
    # Si peu de données, utiliser un modèle simple
    if len(valeurs) < 12:
        print("Attention : données insuffisantes pour modèles complexes")
        modele = 'ar1'
    
    if modele == 'ar1':
        # Modèle AR(1) original
        return modelAR1_original(data)
    
    elif modele == 'auto':
        # Test automatique de plusieurs modèles
        try:
            # Essayer SARIMA d'abord
            if saisonnalite and len(valeurs) >= 12:
                model = SARIMAX(valeurs, order=(1,0,0), seasonal_order=(1,0,0,12))
                results = model.fit(disp=False)
                forecast = results.forecast(steps=12)
            else:
                # Sinon ARIMA simple
                model = ARIMA(valeurs, order=(1,0,0))
                results = model.fit()
                forecast = results.forecast(steps=12)
            
            # Convertir en array numpy (peut être Series ou array)
            if hasattr(forecast, 'values'):
                pred = forecast.values
            else:
                pred = np.array(forecast)
            
        except Exception as e:
            print(f"Modèle complexe échoué ({str(e)}), utilisation du modèle AR(1)")
            return modelAR1_original(data)
    
    elif modele == 'sarima':
        # SARIMA avec saisonnalité
        try:
            if saisonnalite and len(valeurs) >= 12:
                model = SARIMAX(valeurs, order=(1,0,0), seasonal_order=(1,0,0,12))
                results = model.fit(disp=False)
            else:
                model = ARIMA(valeurs, order=(1,0,0))
                results = model.fit()
            
            forecast = results.forecast(steps=12)
            
            # Convertir en array numpy
            if hasattr(forecast, 'values'):
                pred = forecast.values
            else:
                pred = np.array(forecast)
                
        except Exception as e:
            print(f"Modèle SARIMA échoué ({str(e)}), utilisation du modèle AR(1)")
            return modelAR1_original(data)
    
    elif modele == 'arima':
        # Recherche du meilleur ARIMA simple
        try:
            meilleur_aic = np.inf
            meilleur_modele = None
            
            for p in range(0, 3):
                for d in range(0, 2):
                    for q in range(0, 3):
                        try:
                            model = ARIMA(valeurs, order=(p,d,q))
                            results = model.fit()
                            if results.aic < meilleur_aic:
                                meilleur_aic = results.aic
                                meilleur_modele = results
                        except:
                            continue
            
            if meilleur_modele:
                forecast = meilleur_modele.forecast(steps=12)
                # Convertir en array numpy
                if hasattr(forecast, 'values'):
                    pred = forecast.values
                else:
                    pred = np.array(forecast)
            else:
                return modelAR1_original(data)
                
        except Exception as e:
            print(f"Recherche ARIMA échouée ({str(e)}), utilisation du modèle AR(1)")
            return modelAR1_original(data)
    
    else:
        # Mode inconnu, retour au modèle AR(1)
        return modelAR1_original(data)
    
    # Noms des mois futurs (vous pouvez adapter cette logique)
    mois_futurs = [
        "Novembre 2025", "Décembre 2025", "Janvier 2026", "Février 2026", "Mars 2026", "Avril 2026",
        "Mai 2026", "Juin 2026", "Juillet 2026", "Août 2026", "Septembre 2026", "Octobre 2026"
    ]
    
    # Arrondir et créer DataFrame
    df = pd.DataFrame({
        "Mois": mois_futurs,
        "Prévision": np.round(pred).astype(int)
    })
    
    return df

def modelAR1_original(data:dict):
    """Votre fonction AR(1) originale"""
    values = np.array(list(data.values()), dtype=float)
    X_t = values[1:]
    X_lag = values[:-1]
    A = np.vstack([X_lag, np.ones_like(X_lag)]).T
    a, b = np.linalg.lstsq(A, X_t, rcond=None)[0]
    pred = []
    last = values[-1]
    for _ in range(12):
        last = a * last + b
        pred.append(last)
    
    future_months = [
        "Novembre 2025", "Décembre 2025", "Janvier 2026", "Février 2026", "Mars 2026", "Avril 2026",
        "Mai 2026", "Juin 2026", "Juillet 2026", "Août 2026", "Septembre 2026", "Octobre 2026"
    ]
    
    df = pd.DataFrame({
        "Mois": future_months,
        "Prévision AR(1)": np.round(pred).astype(int)
    })
    return df

def comparer_modeles(data:dict):
    """Fonction pour comparer différents modèles"""
    resultats = {}
    
    print("Calcul des prévisions avec différents modèles...")
    
    # 1. Modèle AR(1) original
    print("  - Modèle AR(1)...")
    df_ar1 = modelAR1_original(data)
    resultats['AR(1)'] = df_ar1
    
    # 2. Modèle amélioré avec sélection automatique
    print("  - Modèle auto (SARIMA)...")
    df_auto = modelAR1_ameliore(data, modele='auto', saisonnalite=True)
    resultats['Auto (SARIMA)'] = df_auto
    
    # 3. Modèle ARIMA optimisé
    print("  - Modèle ARIMA optimisé...")
    df_arima = modelAR1_ameliore(data, modele='arima', saisonnalite=False)
    resultats['ARIMA optimisé'] = df_arima
    
    # 4. Modèle SARIMA avec saisonnalité
    print("  - Modèle SARIMA...")
    df_sarima = modelAR1_ameliore(data, modele='sarima', saisonnalite=True)
    resultats['SARIMA'] = df_sarima
    
    # Créer un tableau comparatif
    comparaison = pd.DataFrame()
    comparaison['Mois'] = df_ar1['Mois']
    
    for nom, df in resultats.items():
        if 'Prévision AR(1)' in df.columns:
            comparaison[nom] = df['Prévision AR(1)']
        elif 'Prévision' in df.columns:
            comparaison[nom] = df['Prévision']
        else:
            # Chercher la première colonne numérique
            for col in df.columns:
                if col != 'Mois' and df[col].dtype in [np.int64, np.float64]:
                    comparaison[nom] = df[col]
                    break
    
    return comparaison, resultats

# Fonction simplifiée si vous voulez juste une prévision
def faire_prevision(data:dict, modele='auto'):
    """
    Fonction simplifiée pour faire une prévision
    
    Paramètres:
    -----------
    data : dict
        Dictionnaire des données
    modele : str
        'auto', 'ar1', 'arima', 'sarima'
    """
    return modelAR1_ameliore(data, modele=modele, saisonnalite=True)


def nextMonth(data:dict):
  som = 0
  values = np.array(list(data.values()), dtype=float)
  print("Use : ",values)
  for e in range(len(values)-3, len(values)):
    print(values[e])
    som += values[e]
  return som/3





