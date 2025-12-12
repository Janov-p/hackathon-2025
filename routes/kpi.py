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
    Extraire des KPI depuis un fichier JSON
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
        
        if "filename" not in data:
            return jsonify({"error": "Nom de fichier requis"}), 400
        
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
        
        # Charger et simplifier les données
        target = data.get("target")
        simplified_data = modules['jsonLoader'].simplification(filepath, target)
        
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
        
        # Obtenir la structure pour référence
        full_data = modules['jsonLoader'].loader(filepath)
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
    """
    modules = import_utilities()
    
    if not modules['prevision']:
        return jsonify({"error": "Module prevision non disponible"}), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        # Vérifier les paramètres requis
        required = ['filename', 'target', 'kpi_name']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Champ requis manquant: {field}"}), 400
        
        filename = data['filename']
        config = get_config()
        filepath = os.path.join(config['db_path'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": f"Fichier {filename} non trouvé"}), 404
        
        # Charger les données
        modules['jsonLoader'] = import_utilities()['jsonLoader']
        if not modules['jsonLoader']:
            return jsonify({"error": "Module jsonLoader non disponible"}), 500
        
        # Simplifier les données
        simplified_data = modules['jsonLoader'].simplification(
            filepath, 
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

# ==================== FONCTIONS DE RÉPARTITION INTELLIGENTE ====================

def calculate_auto_allocation(cible, target_mode, objectifs=None, secteur=None):
    """
    Calcule une répartition automatique intelligente basée sur la cible
    """
    # Base allocation par défaut
    base_allocation = {
        'print': 25,
        'digital': 35,
        'social': 25,
        'events': 15
    }
    
    adjustments = {
        'print': 0,
        'digital': 0,
        'social': 0,
        'events': 0
    }
    
    # === AJUSTEMENTS POUR LES PARTICULIERS ===
    if target_mode == 'particuliers':
        # Ajustement par âge
        ages = cible.get('ages', [])
        for age in ages:
            if age in ['18-24', '25-34']:
                adjustments['digital'] += 15
                adjustments['social'] += 10
                adjustments['print'] -= 15
                adjustments['events'] -= 10
            elif age in ['35-44']:
                adjustments['digital'] += 10
                adjustments['social'] += 5
                adjustments['print'] -= 10
                adjustments['events'] -= 5
            elif age in ['45-54']:
                adjustments['digital'] += 5
                adjustments['print'] += 5
                adjustments['social'] -= 5
                adjustments['events'] -= 5
            elif age in ['55-64', '65+']:
                adjustments['print'] += 15
                adjustments['events'] += 5
                adjustments['digital'] -= 10
                adjustments['social'] -= 10
        
        # Ajustement par CSP
        csp_list = cible.get('csp', [])
        for csp in csp_list:
            if csp in ['CSP+', 'Cadres', 'Professions libérales']:
                adjustments['print'] += 10
                adjustments['digital'] += 5
                adjustments['events'] += 5
                adjustments['social'] -= 5
            elif csp in ['CSP-', 'Employés', 'Ouvriers']:
                adjustments['social'] += 10
                adjustments['digital'] += 5
                adjustments['print'] -= 10
                adjustments['events'] -= 5
        
        # Ajustement par centres d'intérêt
        interets = cible.get('centresInteret', [])
        for interet in interets:
            if interet in ['technologie', 'jeux-video', 'cinema']:
                adjustments['digital'] += 15
                adjustments['social'] += 10
                adjustments['events'] -= 10
                adjustments['print'] -= 15
            elif interet in ['voyage', 'gastronomie', 'luxe']:
                adjustments['social'] += 15
                adjustments['digital'] += 10
                adjustments['events'] += 5
                adjustments['print'] -= 5
            elif interet in ['sport', 'nature', 'plein-air']:
                adjustments['events'] += 20
                adjustments['social'] += 5
                adjustments['digital'] -= 10
                adjustments['print'] -= 5
            elif interet in ['culture', 'lecture', 'musique']:
                adjustments['print'] += 10
                adjustments['events'] += 10
                adjustments['digital'] += 5
                adjustments['social'] -= 5
    
    # === AJUSTEMENTS POUR LES PROFESSIONNELS ===
    elif target_mode == 'professionnels':
        # Ajustement par taille d'entreprise
        tailles = cible.get('taillesEntreprise', [])
        for taille in tailles:
            if taille in ['TPE', 'PME']:
                adjustments['digital'] += 20
                adjustments['social'] += 15
                adjustments['events'] -= 10
                adjustments['print'] -= 15
            elif taille in ['ETI']:
                adjustments['digital'] += 10
                adjustments['events'] += 10
                adjustments['print'] += 5
                adjustments['social'] -= 5
            elif taille in ['GE']:
                adjustments['events'] += 20
                adjustments['print'] += 15
                adjustments['digital'] -= 10
                adjustments['social'] -= 15
        
        # Ajustement par secteur
        secteurs = cible.get('secteursCibles', [])
        for secteur_cible in secteurs:
            if secteur_cible in ['Technologie', 'Digital', 'E-commerce']:
                adjustments['digital'] += 25
                adjustments['social'] += 15
                adjustments['events'] -= 15
                adjustments['print'] -= 20
            elif secteur_cible in ['BTP', 'Industrie', 'Manufacturing']:
                adjustments['events'] += 20
                adjustments['print'] += 15
                adjustments['social'] -= 10
                adjustments['digital'] -= 10
            elif secteur_cible in ['Conseil', 'Services', 'Finance']:
                adjustments['events'] += 15
                adjustments['digital'] += 10
                adjustments['print'] += 5
                adjustments['social'] -= 5
            elif secteur_cible in ['Commerce', 'Distribution', 'Retail']:
                adjustments['digital'] += 15
                adjustments['social'] += 10
                adjustments['events'] += 5
                adjustments['print'] -= 5
        
        # Ajustement par fonction
        fonctions = cible.get('fonctions', [])
        for fonction in fonctions:
            if fonction in ['dirigeant', 'CEO', 'PDG']:
                adjustments['events'] += 20
                adjustments['print'] += 15
                adjustments['digital'] -= 10
                adjustments['social'] -= 15
            elif fonction in ['DRH', 'RH']:
                adjustments['social'] += 20
                adjustments['events'] += 10
                adjustments['digital'] += 5
                adjustments['print'] -= 10
            elif fonction in ['marketing', 'commercial', 'ventes']:
                adjustments['digital'] += 20
                adjustments['social'] += 15
                adjustments['events'] += 5
                adjustments['print'] -= 5
            elif fonction in ['technique', 'IT', 'R&D']:
                adjustments['digital'] += 25
                adjustments['social'] += 10
                adjustments['events'] -= 10
                adjustments['print'] -= 15
    
    # === AJUSTEMENTS PAR OBJECTIFS ===
    if objectifs:
        for objectif in objectifs:
            if objectif == 'notoriete':
                adjustments['print'] += 15
                adjustments['events'] += 10
                adjustments['digital'] += 5
                adjustments['social'] -= 5
            elif objectif == 'trafic':
                adjustments['digital'] += 20
                adjustments['social'] += 15
                adjustments['events'] -= 10
                adjustments['print'] -= 10
            elif objectif == 'leads':
                adjustments['digital'] += 25
                adjustments['social'] += 10
                adjustments['events'] += 5
                adjustments['print'] -= 5
            elif objectif == 'conversion':
                adjustments['digital'] += 30
                adjustments['social'] += 10
                adjustments['print'] -= 15
                adjustments['events'] -= 10
            elif objectif == 'fidelisation':
                adjustments['social'] += 25
                adjustments['digital'] += 15
                adjustments['events'] += 10
                adjustments['print'] -= 5
    
    # === AJUSTEMENTS PAR SECTEUR GLOBAL ===
    if secteur:
        secteur_lower = secteur.lower()
        if any(word in secteur_lower for word in ['tech', 'digital', 'web', 'software']):
            adjustments['digital'] += 20
            adjustments['social'] += 15
            adjustments['events'] -= 15
            adjustments['print'] -= 15
        elif any(word in secteur_lower for word in ['conseil', 'service', 'professionnel']):
            adjustments['events'] += 15
            adjustments['print'] += 10
            adjustments['digital'] += 5
            adjustments['social'] -= 5
        elif any(word in secteur_lower for word in ['retail', 'commerce', 'boutique']):
            adjustments['digital'] += 15
            adjustments['social'] += 10
            adjustments['events'] += 5
            adjustments['print'] -= 5
        elif any(word in secteur_lower for word in ['industrie', 'btp', 'construction']):
            adjustments['events'] += 20
            adjustments['print'] += 15
            adjustments['digital'] -= 10
            adjustments['social'] -= 15
    
    # Appliquer les ajustements
    final_allocation = {}
    for channel in base_allocation:
        final_allocation[channel] = base_allocation[channel] + adjustments[channel]
    
    # S'assurer que les valeurs sont entre 0 et 100
    for channel in final_allocation:
        final_allocation[channel] = max(0, min(100, final_allocation[channel]))
    
    # Normaliser pour que la somme fasse 100
    total = sum(final_allocation.values())
    if total != 100:
        for channel in final_allocation:
            final_allocation[channel] = round((final_allocation[channel] / total) * 100, 1)
    
    # Arrondir et vérifier la somme
    final_allocation = {k: round(v, 1) for k, v in final_allocation.items()}
    
    # Ajuster la somme à exactement 100
    diff = 100 - sum(final_allocation.values())
    if diff != 0:
        # Ajouter la différence au canal principal
        main_channel = max(final_allocation, key=final_allocation.get)
        final_allocation[main_channel] = round(final_allocation[main_channel] + diff, 1)
    
    return final_allocation

def suggest_supports(allocation, cible, target_mode):
    """
    Suggère des supports spécifiques basés sur l'allocation et la cible
    """
    supports = {
        'print': [],
        'digital': [],
        'social': [],
        'events': []
    }
    
    # Supports PRINT
    if allocation.get('print', 0) > 10:
        supports['print'].append('quotidien_regional')
        if target_mode == 'professionnels':
            supports['print'].append('magazine_professionnel')
            supports['print'].append('supplement_economique')
        else:
            supports['print'].append('magazine_generaliste')
            if 'ages' in cible and any(age in ['55-64', '65+'] for age in cible['ages']):
                supports['print'].append('quotidien_national')
    
    # Supports DIGITAL
    if allocation.get('digital', 0) > 15:
        supports['digital'].append('display_cible')
        supports['digital'].append('site_web')
        
        if target_mode == 'professionnels':
            supports['digital'].append('linkedin_ads')
            supports['digital'].append('newsletter_pro')
        else:
            supports['digital'].append('google_ads')
            supports['digital'].append('newsletter')
        
        if allocation.get('digital', 0) > 25:
            supports['digital'].append('video_online')
            supports['digital'].append('affiliation')
    
    # Supports SOCIAL
    if allocation.get('social', 0) > 15:
        if target_mode == 'professionnels':
            supports['social'].append('linkedin')
            supports['social'].append('twitter')
        else:
            supports['social'].append('instagram')
            supports['social'].append('facebook')
            
            if 'ages' in cible and any(age in ['18-24', '25-34'] for age in cible['ages']):
                supports['social'].append('tiktok')
                supports['social'].append('snapchat')
        
        if allocation.get('social', 0) > 25:
            supports['social'].append('influenceurs')
            supports['social'].append('communautes_online')
    
    # Supports EVENTS
    if allocation.get('events', 0) > 10:
        if target_mode == 'professionnels':
            supports['events'].append('salon_professionnel')
            supports['events'].append('petit_dejeuner_affaires')
            supports['events'].append('conference_sectorielle')
        else:
            supports['events'].append('evenement_local')
            supports['events'].append('atelier_participatif')
            supports['events'].append('demonstration_produit')
        
        if allocation.get('events', 0) > 20:
            supports['events'].append('sponsoring_evenement')
            supports['events'].append('roadshow')
    
    return supports

def calculate_kpi_targets(budget, allocation, target_mode):
    """
    Calcule des KPI cibles réalistes basés sur le budget et l'allocation
    """
    # Coûts moyens par canal (en € pour 1000 impressions/contacts)
    cost_per_mille = {
        'print': 15,      # € pour 1000 lecteurs
        'digital': 8,     # € pour 1000 impressions
        'social': 12,     # € pour 1000 impressions
        'events': 150     # € par participant
    }
    
    # Calcul du budget par canal
    budgets = {}
    for channel, percentage in allocation.items():
        budgets[channel] = (budget * percentage) / 100
    
    # Estimation des KPI
    estimated_reach = 0
    estimated_impressions = 0
    estimated_participants = 0
    
    for channel, channel_budget in budgets.items():
        if channel == 'events':
            estimated_participants += channel_budget / cost_per_mille[channel]
        else:
            estimated_impressions += (channel_budget / cost_per_mille[channel]) * 1000
    
    # Reach estimé (unique)
    estimated_reach = estimated_impressions / 3  # Approximation: 3 impressions par personne
    
    # Ajustement par mode cible
    if target_mode == 'professionnels':
        estimated_reach *= 0.7  # Audience plus restreinte
        estimated_impressions *= 0.8
    
    return {
        'estimated_reach': round(estimated_reach),
        'estimated_impressions': round(estimated_impressions),
        'estimated_participants': round(estimated_participants),
        'estimated_cpm': round(sum(budgets.values()) / (estimated_impressions / 1000), 2),
        'estimated_cpc': round(sum(budgets.values()) / (estimated_reach * 0.1), 2)  # 10% CTR
    }

@kpi_bp.route('/media/plan', methods=['POST'])
def generate_media_plan():
    """
    Générer un plan média avec répartition intelligente
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        # Vérifier le fichier de campagne
        campaign_file = data.get('campaign_file')
        if not campaign_file:
            return jsonify({"error": "Fichier de campagne requis"}), 400
        
        config = get_config()
        campaign_path = os.path.join(config['db_path'], campaign_file)
        
        if not os.path.exists(campaign_path):
            return jsonify({"error": f"Fichier {campaign_file} non trouvé"}), 404
        
        # Charger la campagne
        with open(campaign_path, 'r', encoding='utf-8') as f:
            campaign = json.load(f)
        
        # Extraire les informations
        form_data = campaign.get('formData', {})
        
        # Budget
        budget = form_data.get('budget', 10000)
        
        # Objectifs
        objectives = form_data.get('objectifs', [])
        
        # Cible
        target = form_data.get('cible', {})
        
        # Mode cible
        target_mode = campaign.get('targetMode', 'particuliers')
        
        # Secteur
        secteur = form_data.get('secteur', '')
        
        # Déterminer la répartition
        if 'budget_allocation' in data:
            # Utiliser la répartition fournie manuellement
            budget_allocation = data['budget_allocation']
            allocation_mode = 'manuel'
        else:
            # Calculer une répartition automatique intelligente
            budget_allocation = calculate_auto_allocation(
                cible=target,
                target_mode=target_mode,
                objectifs=objectives,
                secteur=secteur
            )
            allocation_mode = 'auto_intelligent'
        
        # Vérifier que la somme fait 100%
        total_percentage = sum(budget_allocation.values())
        if abs(total_percentage - 100) > 1:  # Tolérance de 1%
            return jsonify({
                "error": f"La somme des pourcentages doit être 100% (actuellement {total_percentage:.1f}%)"
            }), 400
        
        # Calculer les budgets par canal
        budgets = {
            channel: round((budget * percentage) / 100, 2)
            for channel, percentage in budget_allocation.items()
        }
        
        # Suggérer des supports spécifiques
        suggested_supports = suggest_supports(budget_allocation, target, target_mode)
        
        # Calculer les KPI cibles
        kpi_targets = calculate_kpi_targets(budget, budget_allocation, target_mode)
        
        # Générer des recommandations détaillées
        recommendations = generate_detailed_recommendations(
            budget_allocation, target, target_mode, objectives
        )
        
        # Générer le plan média
        media_plan = {
            "metadata": {
                "campaign_name": form_data.get('nom', 'Sans nom'),
                "client": form_data.get('nomClient', 'Inconnu'),
                "period": {
                    "start": form_data.get('periodeDebut'),
                    "end": form_data.get('periodeFin')
                },
                "allocation_mode": allocation_mode,
                "generated_at": datetime.now().isoformat(),
                "version": "2.0"
            },
            "budget_summary": {
                "total_budget": budget,
                "allocation_percentage": budget_allocation,
                "allocation_amount": budgets,
                "remaining": budget
            },
            "target_analysis": {
                "profile": target,
                "target_mode": target_mode,
                "objectives": objectives,
                "sector": secteur
            },
            "channel_strategy": {
                channel: {
                    "budget": amount,
                    "percentage": budget_allocation[channel],
                    "recommended_supports": suggested_supports.get(channel, []),
                    "rationale": get_channel_rationale(channel, budget_allocation[channel], target, target_mode)
                }
                for channel, amount in budgets.items()
            },
            "kpi_targets": kpi_targets,
            "recommendations": recommendations,
            "timeline": generate_timeline(form_data.get('periodeDebut'), form_data.get('periodeFin')),
            "optimization_tips": get_optimization_tips(budget_allocation, target_mode)
        }
        
        return jsonify({
            "message": "Plan média généré avec succès",
            "allocation_mode": allocation_mode,
            "media_plan": media_plan
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            "error": f"Erreur: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

# ==================== FONCTIONS SUPPLEMENTAIRES ====================

def generate_detailed_recommendations(allocation, cible, target_mode, objectives):
    """Génère des recommandations détaillées basées sur l'analyse"""
    recommendations = []
    
    # Recommandations par canal
    for channel, percentage in allocation.items():
        if percentage > 25:
            if channel == 'digital':
                recommendations.append(f"Focus digital ({percentage}%) : Privilégiez le marketing automatisé et le retargeting")
            elif channel == 'social':
                recommendations.append(f"Focus réseaux sociaux ({percentage}%) : Développez une stratégie de contenu régulier")
            elif channel == 'events':
                recommendations.append(f"Focus événements ({percentage}%) : Planifiez des rencontres physiques pour fidéliser")
            elif channel == 'print':
                recommendations.append(f"Focus print ({percentage}%) : Utilisez des supports prestigieux pour l'image de marque")
    
    # Recommandations par objectif
    for objective in objectives:
        if objective == 'notoriete':
            recommendations.append("Pour la notoriété : Message simple et répétition sur les médias massifs")
        elif objective == 'leads':
            recommendations.append("Pour les leads : Formulaires optimisés et call-to-action clairs")
        elif objective == 'trafic':
            recommendations.append("Pour le trafic : SEO et contenu viral sur les réseaux sociaux")
    
    # Recommandations par cible
    if target_mode == 'particuliers':
        if 'ages' in cible and any(age in ['18-24', '25-34'] for age in cible['ages']):
            recommendations.append("Cible jeune : Utilisez le storytelling et l'humour sur les réseaux sociaux")
    
    return list(set(recommendations))  # Supprimer les doublons

def get_channel_rationale(channel, percentage, cible, target_mode):
    """Fournit la justification pour l'allocation d'un canal"""
    rationales = {
        'digital': f"Allocation de {percentage}% pour le digital, adapté aux cibles connectées et pour un suivi précis des performances.",
        'social': f"Allocation de {percentage}% pour les réseaux sociaux, idéal pour l'engagement et la création de communauté.",
        'print': f"Allocation de {percentage}% pour le print, efficace pour la crédibilité et la mémorisation à long terme.",
        'events': f"Allocation de {percentage}% pour les événements, parfait pour les relations directes et la fidélisation."
    }
    
    return rationales.get(channel, f"Allocation standard de {percentage}% pour ce canal.")

def generate_timeline(start_date, end_date):
    """Génère un timeline basé sur les dates de la campagne"""
    return {
        "phase_1": {"name": "Préparation & Créatifs", "duration": "2-3 semaines"},
        "phase_2": {"name": "Lancement & Activation", "duration": "1-2 semaines"},
        "phase_3": {"name": "Croissance & Optimisation", "duration": "4-6 semaines"},
        "phase_4": {"name": "Consolidation & Analyse", "duration": "1-2 semaines"}
    }

def get_optimization_tips(allocation, target_mode):
    """Fournit des conseils d'optimisation"""
    tips = []
    
    if allocation.get('digital', 0) > 20:
        tips.append("Digital : Testez A/B vos landing pages et optimisez pour le mobile")
    
    if allocation.get('social', 0) > 20:
        tips.append("Social : Planifiez votre contenu à l'avance et réagissez aux trends")
    
    if target_mode == 'professionnels':
        tips.append("B2B : Privilégiez le marketing d'account et les relations personnalisées")
    
    return tips