from flask import Flask, jsonify
from flask_cors import CORS
import os
import sys

app = Flask(__name__)
CORS(app)  # Pour autoriser les requêtes cross-origin

# Ajouter les chemins aux modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'Utilities'))
sys.path.append(os.path.join(BASE_DIR, 'Calculate'))

# Configuration
app.config['BASE_DIR'] = BASE_DIR
app.config['DB_PATH'] = os.path.join(BASE_DIR, 'db')
app.config['UTILITIES_PATH'] = os.path.join(BASE_DIR, 'Utilities')
app.config['CALCULATE_PATH'] = os.path.join(BASE_DIR, 'Calculate')

print(f"DB Path: {app.config['DB_PATH']}")
print(f"Utilities Path: {app.config['UTILITIES_PATH']}")
print(f"Calculate Path: {app.config['CALCULATE_PATH']}")

# Vérifier si les dossiers existent
for path_name, path in [
    ('DB', app.config['DB_PATH']),
    ('Utilities', app.config['UTILITIES_PATH']),
    ('Calculate', app.config['CALCULATE_PATH'])
]:
    if os.path.exists(path):
        print(f"✓ {path_name} directory exists: {path}")
    else:
        print(f"✗ {path_name} directory NOT FOUND: {path}")

# Importer les routes
try:
    from routes.kpi import kpi_bp
    app.register_blueprint(kpi_bp, url_prefix='/api')
    print("✓ Routes loaded successfully")
except ImportError as e:
    print(f"✗ Error loading routes: {e}")

@app.route('/')
def index():
    return jsonify({
        "API": "Extracteur KPI & Plan Média",
        "version": "1.0",
        "structure": {
            "project_root": BASE_DIR,
            "db": app.config['DB_PATH'],
            "utilities": app.config['UTILITIES_PATH'],
            "calculate": app.config['CALCULATE_PATH']
        },
        "endpoints": {
            "kpi": {
                "POST /api/kpi/extract": "Extraire des KPI",
                "GET /api/kpi/files": "Liste des fichiers disponibles",
                "GET /api/kpi/structure/<filename>": "Structure d'un fichier",
                "GET /api/kpi/fields/<filename>": "Champs disponibles"
            },
            "media": {
                "POST /api/media/plan": "Générer un plan média",
                "GET /api/media/templates": "Modèles de plan média"
            },
            "calculate": {
                "POST /api/calculate/prevision": "Faire des prévisions",
                "GET /api/calculate/models": "Modèles disponibles"
            },
            "system": {
                "GET /api/health": "État du système",
                "GET /api/structure": "Structure du projet"
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')