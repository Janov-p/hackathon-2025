from flask import Blueprint, request, jsonify
import uuid
import json
import os
from datetime import datetime
from flask import current_app

campagnes_bp = Blueprint('campagnes', __name__)

def get_db_path():
    """Retourne le chemin du dossier db"""
    return current_app.config.get('DB_PATH', os.path.join(os.path.dirname(__file__), '..', 'db'))

def sauvegarder_campagne(campagne_id, data):
    """Sauvegarde une campagne dans un fichier JSON"""
    db_path = get_db_path()
    fichier_campagne = os.path.join(db_path, f"campagne_{campagne_id}.json")
    
    with open(fichier_campagne, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return fichier_campagne

def charger_campagne(campagne_id):
    """Charge une campagne depuis un fichier JSON"""
    db_path = get_db_path()
    fichier_campagne = os.path.join(db_path, f"campagne_{campagne_id}.json")
    
    if os.path.exists(fichier_campagne):
        with open(fichier_campagne, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def lister_fichiers_campagnes():
    """Liste tous les fichiers de campagne"""
    db_path = get_db_path()
    fichiers = []
    
    if os.path.exists(db_path):
        for fichier in os.listdir(db_path):
            if fichier.startswith('campagne_') and fichier.endswith('.json'):
                fichiers.append(fichier)
    
    return fichiers

@campagnes_bp.route('/campagnes', methods=['POST'])
def creer_campagne():
    """Créer une nouvelle campagne"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        # Vérification des champs obligatoires
        required_fields = ["targetMode", "repartitionMode", "formData"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Champ manquant: {field}"}), 400
        
        # Vérification des champs dans formData
        form_required = ["nomClient", "nom", "budget", "periodeDebut", "periodeFin"]
        for field in form_required:
            if field not in data["formData"]:
                return jsonify({"error": f"Champ manquant dans formData: {field}"}), 400
        
        # Générer ID
        campagne_id = str(uuid.uuid4())[:8]
        
        # Ajouter métadonnées
        campagne_complete = {
            "id": campagne_id,
            "date_creation": datetime.now().isoformat(),
            "status": "en_attente",
            **data
        }
        
        # Sauvegarder dans db/
        fichier_sauvegarde = sauvegarder_campagne(campagne_id, campagne_complete)
        
        return jsonify({
            "message": "Campagne créée avec succès",
            "campagne_id": campagne_id,
            "fichier": os.path.basename(fichier_sauvegarde),
            "details": {
                "client": data["formData"]["nomClient"],
                "nom": data["formData"]["nom"],
                "budget": f"{data['formData']['budget']}€",
                "periode": f"{data['formData']['periodeDebut']} au {data['formData']['periodeFin']}"
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@campagnes_bp.route('/campagnes', methods=['GET'])
def lister_campagnes():
    """Lister toutes les campagnes"""
    try:
        fichiers = lister_fichiers_campagnes()
        campagnes = []
        
        for fichier in fichiers:
            campagne_id = fichier.replace('campagne_', '').replace('.json', '')
            data = charger_campagne(campagne_id)
            
            if data:
                campagnes.append({
                    "id": campagne_id,
                    "nom": data["formData"]["nom"],
                    "client": data["formData"]["nomClient"],
                    "targetMode": data["targetMode"],
                    "repartitionMode": data["repartitionMode"],
                    "budget": data["formData"]["budget"],
                    "status": data.get("status", "inconnu"),
                    "date_creation": data.get("date_creation")
                })
        
        return jsonify({
            "total": len(campagnes),
            "campagnes": campagnes
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@campagnes_bp.route('/campagnes/<campagne_id>', methods=['GET'])
def recuperer_campagne(campagne_id):
    """Récupérer une campagne par son ID"""
    data = charger_campagne(campagne_id)
    
    if data:
        return jsonify(data), 200
    
    return jsonify({"error": "Campagne non trouvée"}), 404

@campagnes_bp.route('/campagnes/<campagne_id>', methods=['PUT'])
def mettre_a_jour_campagne(campagne_id):
    """Mettre à jour une campagne"""
    try:
        data = charger_campagne(campagne_id)
        
        if not data:
            return jsonify({"error": "Campagne non trouvée"}), 404
        
        nouvelles_donnees = request.get_json()
        
        if not nouvelles_donnees:
            return jsonify({"error": "Données de mise à jour requises"}), 400
        
        # Fusionner les données (mise à jour partielle)
        data.update(nouvelles_donnees)
        data["date_modification"] = datetime.now().isoformat()
        
        # Sauvegarder
        sauvegarder_campagne(campagne_id, data)
        
        return jsonify({
            "message": "Campagne mise à jour",
            "campagne_id": campagne_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@campagnes_bp.route('/campagnes/<campagne_id>/status', methods=['PUT'])
def mettre_a_jour_status(campagne_id):
    """Mettre à jour uniquement le statut"""
    try:
        data = charger_campagne(campagne_id)
        
        if not data:
            return jsonify({"error": "Campagne non trouvée"}), 404
        
        nouvelles_donnees = request.get_json()
        
        if not nouvelles_donnees or "status" not in nouvelles_donnees:
            return jsonify({"error": "Nouveau statut requis"}), 400
        
        statuts_autorises = ["en_attente", "approuvee", "en_cours", "terminee", "annulee"]
        if nouvelles_donnees["status"] not in statuts_autorises:
            return jsonify({"error": f"Statut invalide. Options: {statuts_autorises}"}), 400
        
        data["status"] = nouvelles_donnees["status"]
        data["date_modification"] = datetime.now().isoformat()
        
        sauvegarder_campagne(campagne_id, data)
        
        return jsonify({
            "message": "Statut mis à jour",
            "campagne_id": campagne_id,
            "nouveau_status": data["status"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@campagnes_bp.route('/modeles', methods=['GET'])
def lister_modeles():
    """Lister tous les modèles JSON disponibles dans db/"""
    try:
        db_path = get_db_path()
        fichiers = []
        
        if os.path.exists(db_path):
            for fichier in os.listdir(db_path):
                if fichier.endswith('.json') and not fichier.startswith('campagne_'):
                    chemin_complet = os.path.join(db_path, fichier)
                    with open(chemin_complet, 'r', encoding='utf-8') as f:
                        try:
                            contenu = json.load(f)
                            fichiers.append({
                                "nom": fichier,
                                "client": contenu.get("formData", {}).get("nomClient", "Inconnu"),
                                "targetMode": contenu.get("targetMode"),
                                "repartitionMode": contenu.get("repartitionMode")
                            })
                        except:
                            fichiers.append({"nom": fichier, "error": "Fichier JSON invalide"})
        
        return jsonify({
            "total": len(fichiers),
            "modeles": fichiers
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@campagnes_bp.route('/health', methods=['GET'])
def health_check():
    """Vérification de santé de l'API"""
    db_path = get_db_path()
    db_exists = os.path.exists(db_path)
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "db_access": db_exists,
        "db_path": db_path
    }), 200