from flask import Blueprint, request, jsonify
import os
import json
import sys
from datetime import datetime

kpi_bp = Blueprint('kpi', __name__)

def get_config():
    """Récupère la configuration depuis l'application Flask"""
    from flask import current_app
    return {
        'db_path': current_app.config.get('DB_PATH'),
        'utilities_path': current_app.config.get('UTILITIES_PATH'),
        'calculate_path': current_app.config.get('CALCULATE_PATH'),
        'base_dir': current_app.config.get('BASE_DIR')
    }

def import_utilities():
    """Importe les utilitaires avec gestion d'erreurs"""
    config = get_config()
    
    # S'assurer que les chemins sont dans sys.path
    for path in [config['utilities_path'], config['calculate_path']]:
        if path and path not in sys.path:
            sys.path.append(path)
    
    modules = {}
    
    # Importer jsonLoader
    try:
        import jsonLoader as js
        modules['jsonLoader'] = js
    except ImportError as e:
        print(f"Error importing jsonLoader: {e}")
        modules['jsonLoader'] = None
    
    # Importer extractMeasure
    try:
        import extractMeasure as em
        modules['extractMeasure'] = em
    except ImportError as e:
        print(f"Error importing extractMeasure: {e}")
        modules['extractMeasure'] = None
    
    # Importer prevision
    try:
        import prevision as pv
        modules['prevision'] = pv
    except ImportError as e:
        print(f"Error importing prevision: {e}")
        modules['prevision'] = None
    
    return modules

# ==================== ROUTES SYSTÈME ====================

@kpi_bp.route('/health', methods=['GET'])
def health_check():
    """Vérification de l'état du système"""
    config = get_config()
    
    # Vérifier l'existence des dossiers
    folders = {
        'db': os.path.exists(config['db_path']),
        'utilities': os.path.exists(config['utilities_path']),
        'calculate': os.path.exists(config['calculate_path'])
    }
    
    # Vérifier l'existence des fichiers
    utility_files = []
    if folders['utilities']:
        utility_files = [f for f in os.listdir(config['utilities_path']) 
                        if f.endswith('.py')]
    
    db_files = []
    if folders['db']:
        db_files = [f for f in os.listdir(config['db_path']) 
                   if f.endswith('.json')]
    
    # Tester les imports
    modules = import_utilities()
    modules_status = {name: module is not None 
                     for name, module in modules.items()}
    
    return jsonify({
        "status": "ok" if all(folders.values()) else "warning",
        "timestamp": datetime.now().isoformat(),
        "folders": folders,
        "files": {
            "utilities": utility_files,
            "db": db_files[:10],  # Limiter à 10 fichiers
            "total_db_files": len(db_files)
        },
        "modules": modules_status,
        "python_path": sys.path
    }), 200

@kpi_bp.route('/structure', methods=['GET'])
def project_structure():
    """Affiche la structure du projet"""
    config = get_config()
    
    def list_dir(path, indent=0):
        """Liste récursivement un dossier"""
        result = []
        if os.path.exists(path):
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    result.append({
                        "type": "directory",
                        "name": item,
                        "path": item_path,
                        "children": list_dir(item_path, indent + 1)
                    })
                else:
                    result.append({
                        "type": "file",
                        "name": item,
                        "path": item_path,
                        "size_kb": round(os.path.getsize(item_path) / 1024, 2)
                    })
        return result
    
    structure = {
        "base": config['base_dir'],
        "db": list_dir(config['db_path'])[:20],  # Limiter
        "utilities": list_dir(config['utilities_path']),
        "calculate": list_dir(config['calculate_path']),
        "routes": list_dir(os.path.join(config['base_dir'], 'routes'))
    }
    
    return jsonify(structure), 200

# ==================== ROUTES KPI ====================

@kpi_bp.route('/kpi/extract', methods=['POST'])
def extract_kpi():
    """
    Extraire des KPI depuis un fichier JSON ou depuis des données JSON directes
    """
    modules = import_utilities()
    
    if not modules['jsonLoader'] or not modules['extractMeasure']:
        return jsonify({
            "error": "Modules manquants",
            "jsonLoader_available": modules['jsonLoader'] is not None,
            "extractMeasure_available": modules['extractMeasure'] is not None
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        # Vérifier si on a des données JSON directes ou un fichier
        if "json_data" in data:
            json_content = data["json_data"]
            filename = "direct_json"
        elif "filename" in data:
            filename = data["filename"]
            config = get_config()
            filepath = os.path.join(config['db_path'], filename)
            
            if not os.path.exists(filepath):
                available = [f for f in os.listdir(config['db_path']) 
                            if f.endswith('.json')]
                return jsonify({
                    "error": f"Fichier {filename} non trouvé",
                    "available_files": available
                }), 404
            json_content = filepath
        else:
            return jsonify({"error": "Soit 'filename' soit 'json_data' doit être fourni"}), 400
        
        target = data.get("target")
        simplified_data = modules['jsonLoader'].simplification(json_content, target)
        
        if not simplified_data:
            return jsonify({
                "error": "Impossible de simplifier les données",
                "filename": filename,
                "target": target
            }), 400
        
        # Extraire les KPI demandés
        extractions = data.get("extractions", [])
        results = []
        
        for extraction in extractions:
            if "level1" in extraction and "level2" in extraction:
                try:
                    kpi_value = modules['extractMeasure'].extractDataOneNext(
                        simplified_data, 
                        extraction["level1"], 
                        extraction["level2"]
                    )
                    
                    results.append({
                        "level1": extraction["level1"],
                        "level2": extraction["level2"],
                        "value": kpi_value,
                        "type": type(kpi_value).__name__
                    })
                except Exception as e:
                    results.append({
                        "level1": extraction["level1"],
                        "level2": extraction["level2"],
                        "error": str(e),
                        "value": None
                    })
        
        # Obtenir la structure pour référence (uniquement pour les fichiers)
        if isinstance(json_content, str) and json_content != "direct_json":
            full_data = modules['jsonLoader'].loader(json_content)
            all_paths = modules['jsonLoader'].collect_subdicts_with_paths(full_data)
            available_paths = modules['jsonLoader'].getDataPathNames(all_paths)
        else:
            # Pour les données directes, on essaie de collecter les chemins
            full_data = modules['jsonLoader'].loader(json_content)
            all_paths = modules['jsonLoader'].collect_subdicts_with_paths(full_data)
            available_paths = modules['jsonLoader'].getDataPathNames(all_paths)
        
        return jsonify({
            "filename": filename,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "extractions": results,
            "available_fields": available_paths[:50],
            "total_fields": len(available_paths),
            "sample_data": {
                "first_keys": list(simplified_data.keys())[:5] 
                if isinstance(simplified_data, dict) else []
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@kpi_bp.route('/kpi/files', methods=['GET'])
def list_json_files():
    """Liste tous les fichiers JSON disponibles"""
    try:
        config = get_config()
        
        if not os.path.exists(config['db_path']):
            return jsonify({"error": "Dossier db non trouvé"}), 404
        
        files = []
        for filename in os.listdir(config['db_path']):
            if filename.endswith('.json'):
                filepath = os.path.join(config['db_path'], filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    
                    # Analyser le type de fichier
                    file_type = "unknown"
                    if isinstance(content, dict):
                        if "formData" in content:
                            file_type = "campaign"
                        elif any(key in content for key in ["femme", "homme", "ensemble"]):
                            file_type = "kpi_data"
                        elif "targetMode" in content:
                            file_type = "campaign_template"
                    
                    files.append({
                        "filename": filename,
                        "type": file_type,
                        "size_kb": round(os.path.getsize(filepath) / 1024, 2),
                        "last_modified": datetime.fromtimestamp(
                            os.path.getmtime(filepath)
                        ).isoformat()
                    })
                except json.JSONDecodeError:
                    files.append({
                        "filename": filename,
                        "error": "Invalid JSON"
                    })
                except Exception as e:
                    files.append({
                        "filename": filename,
                        "error": str(e)
                    })
        
        # Trier par nom
        files.sort(key=lambda x: x['filename'])
        
        return jsonify({
            "path": config['db_path'],
            "total": len(files),
            "files": files
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@kpi_bp.route('/kpi/fields/<filename>', methods=['GET'])
def get_available_fields(filename):
    """Obtenir tous les champs disponibles dans un fichier"""
    modules = import_utilities()
    
    if not modules['jsonLoader']:
        return jsonify({"error": "Module jsonLoader non disponible"}), 500
    
    try:
        config = get_config()
        filepath = os.path.join(config['db_path'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Fichier non trouvé"}), 404
        
        # Charger le fichier
        data = modules['jsonLoader'].loader(filepath)
        
        if not data:
            return jsonify({"error": "Impossible de charger le fichier"}), 400
        
        # Obtenir tous les chemins
        all_paths = modules['jsonLoader'].collect_subdicts_with_paths(data)
        available_paths = modules['jsonLoader'].getDataPathNames(all_paths)
        
        # Grouper par niveau
        grouped = {}
        for path in available_paths:
            # Extraire des informations sur le chemin
            parts = path.split('_') if '_' in path else [path]
            first_part = parts[0]
            
            if first_part not in grouped:
                grouped[first_part] = []
            grouped[first_part].append(path)
        
        # Obtenir un échantillon de données pour les premiers champs
        sample_data = {}
        for field in available_paths[:10]:  # 10 premiers champs
            extracted = modules['jsonLoader'].collectData(all_paths, field)
            if extracted and isinstance(extracted, dict):
                sample_data[field] = {
                    "keys": list(extracted.keys())[:5],
                    "type": "dict",
                    "keys_count": len(extracted)
                }
            elif extracted:
                sample_data[field] = {
                    "value": extracted,
                    "type": type(extracted).__name__
                }
        
        return jsonify({
            "filename": filename,
            "total_fields": len(available_paths),
            "fields": available_paths,
            "grouped_fields": {k: len(v) for k, v in grouped.items()},
            "sample_data": sample_data,
            "root_structure": list(data.keys()) if isinstance(data, dict) else []
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== ROUTES CALCULATE ====================

@kpi_bp.route('/calculate/prevision', methods=['POST'])
def calculate_prevision():
    """
    Effectuer des prévisions avec le module prevision
    Accepte soit un fichier (filename) soit des données JSON (json_data)
    """
    modules = import_utilities()
    
    if not modules['prevision']:
        return jsonify({"error": "Module prevision non disponible"}), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        # Vérifier les paramètres requis
        required = ['target', 'kpi_name']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Champ requis manquant: {field}"}), 400
        
        # Vérifier si on a des données JSON directes ou un fichier
        if "json_data" in data:
            json_content = data["json_data"]
            filename = "direct_json"
        elif "filename" in data:
            filename = data['filename']
            config = get_config()
            filepath = os.path.join(config['db_path'], filename)
            
            if not os.path.exists(filepath):
                return jsonify({"error": f"Fichier {filename} non trouvé"}), 404
            json_content = filepath
        else:
            return jsonify({"error": "Soit 'filename' soit 'json_data' doit être fourni"}), 400
        
        # Charger les données
        modules['jsonLoader'] = import_utilities()['jsonLoader']
        if not modules['jsonLoader']:
            return jsonify({"error": "Module jsonLoader non disponible"}), 500
        
        # Simplifier les données
        simplified_data = modules['jsonLoader'].simplification(
            json_content, 
            data['target']
        )
        
        if not simplified_data:
            return jsonify({
                "error": "Impossible de simplifier les données",
                "filename": filename,
                "target": data['target']
            }), 400
        
        # Extraire la série temporelle
        kpi_series = modules['extractMeasure'].extractDataOneNext(
            simplified_data,
            data.get('level1', 'ensemble'),
            data['kpi_name']
        )
        
        if not kpi_series:
            return jsonify({
                "error": f"KPI '{data['kpi_name']}' non trouvé"
            }), 404
        
        # Effectuer la prévision
        # Note: Vous devrez adapter cela en fonction de votre module prevision
        forecast_result = {
            "original_data": kpi_series,
            "forecast": [],  # À remplacer par votre logique de prévision
            "model_used": "AR1",  # Exemple
            "parameters": data.get('parameters', {})
        }
        
        # Si votre module prevision a une fonction spécifique
        if hasattr(modules['prevision'], 'modelAR1'):
            forecast_result['model_info'] = str(modules['prevision'].modelAR1)
        
        return jsonify({
            "filename": filename,
            "target": data['target'],
            "kpi": data['kpi_name'],
            "timestamp": datetime.now().isoformat(),
            "forecast": forecast_result,
            "data_points": len(kpi_series) if hasattr(kpi_series, '__len__') else 1
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur dans le calcul: {str(e)}"}), 500

@kpi_bp.route('/calculate/models', methods=['GET'])
def list_calculation_models():
    """Liste les modèles de calcul disponibles"""
    modules = import_utilities()
    
    models = []
    
    if modules['prevision']:
        # Inspecter le module prevision pour trouver les modèles
        import inspect
        
        for name, obj in inspect.getmembers(modules['prevision']):
            if not name.startswith('_') and not inspect.ismodule(obj):
                models.append({
                    "name": name,
                    "type": type(obj).__name__
                })
    
    return jsonify({
        "module_available": modules['prevision'] is not None,
        "models": models,
        "total_models": len(models)
    }), 200