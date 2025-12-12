from flask import Blueprint, request, jsonify, current_app
import os
import json
from datetime import datetime

media_bp = Blueprint('media', __name__)

def get_config():
    """Récupère la configuration depuis l'application Flask"""
    return {
        'db_path': current_app.config.get('DB_PATH'),
        'utilities_path': current_app.config.get('UTILITIES_PATH'),
        'calculate_path': current_app.config.get('CALCULATE_PATH'),
        'base_dir': current_app.config.get('BASE_DIR')
    }

def load_json_data(filename):
    """Charge un fichier JSON depuis le dossier db"""
    config = get_config()
    file_path = os.path.join(config['db_path'], filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_available_options():
    """Récupère les options disponibles depuis tarif_CMP.json"""
    tarifs = load_json_data('tarif_CMP.json')
    if not tarifs:
        return {}
    
    options = {
        'print': [],
        'digital': [
            {'id': 'habillage', 'name': 'Habillage site', 'cpm': 15, 'baseImpressions': 2500000},
            {'id': 'pave', 'name': 'Pavé', 'cpm': 8, 'baseImpressions': 2500000},
            {'id': 'interstitiel', 'name': 'Interstitiel appli', 'cpm': 12, 'baseImpressions': 400000},
            {'id': 'smart_cover', 'name': 'Smart cover mobile', 'cpm': 10, 'baseImpressions': 400000},
            {'id': 'preroll', 'name': 'Pré-roll vidéo', 'cpm': 20, 'baseImpressions': 300000}
        ],
        'social': [
            {'id': 'instagram', 'name': 'Instagram', 'cpm': 6, 'baseImpressions': 250000},
            {'id': 'facebook', 'name': 'Facebook', 'cpm': 5, 'baseImpressions': 250000},
            {'id': 'linkedIn', 'name': 'LinkedIn', 'cpm': 7, 'baseImpressions': 200000},
            {'id': 'twitter', 'name': 'Twitter', 'cpm': 6, 'baseImpressions': 200000},
            {'id': 'video_social', 'name': 'Vidéo réseaux sociaux', 'cpm': 8, 'baseImpressions': 150000}
        ]
    }
    
    # Extraction simplifiée pour Print (Corse Matin)
    cm_section = tarifs.get('feuilles', {}).get('PRIVILEGE_CM', {}).get('sections', {})
    
    # Formats standards Corse Matin
    cm_formats = [
        {'id': 'page_une_module_1', 'name': 'Une - Module 1', 'tarif': 1100, 'baseImpressions': 130000},
        {'id': 'page_une_module_2', 'name': 'Une - Module 2', 'tarif': 2100, 'baseImpressions': 130000},
        {'id': 'pleine_page', 'name': 'Pleine Page (Privilège)', 'tarif': 8000, 'baseImpressions': 130000},
        {'id': 'demi_page', 'name': 'Demi Page (Privilège)', 'tarif': 4100, 'baseImpressions': 130000},
        {'id': 'un_quart_page', 'name': '1/4 Page (Privilège)', 'tarif': 1900, 'baseImpressions': 130000},
        {'id': 'bandeau', 'name': 'Bandeau (Privilège)', 'tarif': 1500, 'baseImpressions': 130000}
    ]
    options['print'].extend(cm_formats)
    
    # Diverto
    diverto = tarifs.get('feuilles', {}).get('DIVERTO_MOD_PUB', {}).get('modules', {})
    if diverto:
        options['print'].append({'id': 'diverto_page', 'name': 'Diverto - Page', 'tarif': diverto.get('page_complete', {}).get('tarif', 1000), 'baseImpressions': 231000}) # Reach Diverto approx
        options['print'].append({'id': 'diverto_demi', 'name': 'Diverto - 1/2 Page', 'tarif': diverto.get('demi_page', {}).get('tarif', 600), 'baseImpressions': 231000})

    # Version Femina
    femina = tarifs.get('feuilles', {}).get('FEMINA_Modules_Pub', {}).get('modules', {})
    if femina:
        options['print'].append({'id': 'femina_page', 'name': 'Femina - Page', 'tarif': femina.get('page_complete', {}).get('tarif', 1000), 'baseImpressions': 218600}) # Reach Femina approx
        options['print'].append({'id': 'femina_demi', 'name': 'Femina - 1/2 Page', 'tarif': femina.get('demi_page', {}).get('tarif', 600), 'baseImpressions': 218600})

    # Settimana (exemple, data non extraite spécifiquement mais mentionnée)
    settimana = tarifs.get('feuilles', {}).get('SETTIMANA', {}).get('sections', {})
    if settimana:
        options['print'].append({'id': 'settimana_page', 'name': 'Settimana - Page', 'tarif': 2000, 'baseImpressions': 50000}) # Estimation

    return options

def get_audience_metrics():
    """Charge les données d'audience depuis les JSON"""
    metrics = {
        'corse_matin': 147000, # Par défaut
        'diverto': 231000,
        'femina': 218600,
        'social': {}
    }
    
    # Charger audience.json
    aud = load_json_data('audience.json')
    if aud:
        cm_val = aud.get('donnees_principales', {}).get('cible_ensemble', {}).get('corse_matin_valeur', 147)
        metrics['corse_matin'] = cm_val * 1000
        
    # Charger Diverto
    div = load_json_data('Diverto_OneNext.json')
    if div:
        metrics['diverto'] = int(div.get('donnees_globales', {}).get('ensemble', {}).get('milliers', 231)) * 1000
        
    # Charger Femina
    vf = load_json_data('VF_OneNext.json')
    if vf:
        metrics['femina'] = int(vf.get('donnees_globales', {}).get('ensemble', {}).get('milliers', 218)) * 1000
        
    # Charger RS
    rs = load_json_data('RS.json')
    if rs:
        metrics['social'] = rs.get('moyennes_annuelles', {})
        
    return metrics

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

def calculate_kpi_targets(budget, allocation, target=None, items=None):
    """
    Calcule des KPI cibles réalistes basés sur le budget et l'allocation OU la liste des items
    Prend en compte le ciblage (target) pour pondérer l'audience
    """
    audience_data = get_audience_metrics()
    
    # Extraction des critères de ciblage
    target_criteria = {}
    target_mode = 'particuliers'
    if target:
        target_mode = target.get('targetMode', 'particuliers')
        target_criteria = target.get('criteria', {})
        print(f"DEBUG: Computing KPIs with target criteria: {target_criteria} for mode {target_mode}")

    
    estimated_reach = 0
    estimated_impressions = 0
    estimated_cost = 0

    # Fonction locale pour récupérer l'audience ciblée précise
    def get_targeted_audience(media_type, criteria):
        """
        Calcule l'audience ciblée en utilisant les données brutes JSON.
        Gère le croisement Age x Sexe x CSP selon les disponibilités des fichiers.
        """
        base_audience = audience_data.get(media_type, 0)
        
        # Si pas de critères, retour audience globale
        if not criteria or (not criteria.get('age') and not criteria.get('sexe') and not criteria.get('csp')):
            return base_audience

        # Chargement des données détaillées selon le média
        details = None
        if media_type == 'diverto':
            details = load_json_data('Diverto_OneNext.json')
        elif media_type == 'femina':
            details = load_json_data('VF_OneNext.json')
        elif media_type == 'corse_matin':
            details = load_json_data('audience.json')
            
        if not details: 
            # Fallback si pas de fichier détail ou média social (pas de JSON détaillé structuré pareil)
            # On utilise l'affinité simplifiée implémentée précédemment (ou une version simplifiée ici)
            return base_audience * get_affinity_coefficient(media_type, criteria)

        # === LOGIQUE POUR ONE NEXT (Femina, Diverto) ===
        if media_type in ['femina', 'diverto']:
            # Ces fichiers permettent le croisement Age x Sexe (ex: age -> 35_a_49_ans -> femmes)
            # Clés Sexe JSON: 'hommes', 'femmes', 'ensemble'
            # Clés Age JSON: '15_a_24_ans', ...
            
            # 1. Déterminer les colonnes Sexe à sommer
            sex_keys = []
            if not criteria.get('sexe'):
                sex_keys = ['ensemble'] # Si pas de filtre sexe, on prend tout
            else:
                for s in criteria['sexe']:
                    if s == 'homme': sex_keys.append('hommes')
                    elif s == 'femme': sex_keys.append('femmes')
            
            # 2. Déterminer les lignes Age à sommer
            age_keys = []
            if criteria.get('age'):
                # Mapping Frontend -> JSON OneNext
                mapping_age = {
                    '15_24_ans': '15_a_24_ans',
                    '25_34_ans': '25_a_34_ans',
                    '35_49_ans': '35_a_49_ans',
                    '50_64_ans': '50_a_59_ans', # Partition approx (JSON a 50-59 et 60+)
                    '65_ans_ou_plus': '60_ans_et_plus'
                }
                for a in criteria['age']:
                    if a in mapping_age: age_keys.append(mapping_age[a])
                    if a == '50_64_ans': # Cas spécial: 50-64 couvre 50-59 partiellement et 60+ partiellement
                        # Pour simplifier avec les clés dispo, on a mappé sur 50-59.
                        # Idéalement il faudrait splitter. On accepte l'approx.
                        pass
            
            # Calcul Somme
            total_audience = 0
            
            if not age_keys: 
                # Pas de filtre age, on regarde juste le sexe global
                for sk in sex_keys:
                    # On prend directement le total par sexe dans 'donnees_globales' ou 'sexe'
                    # Le JSON a une section 'sexe' -> 'femme' -> 'ensemble'
                    # Plus simple: utiliser donnees_globales si dispo
                    if sk == 'ensemble': val = details['donnees_globales']['ensemble']['milliers']
                    elif sk == 'hommes': val = details['donnees_globales']['hommes']['milliers']
                    elif sk == 'femmes': val = details['donnees_globales']['femmes']['milliers']
                    else: val = 0
                    if not criteria.get('sexe'): # Si ensemble, on prend juste ensemble une fois
                         total_audience = val
                         break
                    total_audience += val
            else:
                # Filtre Age (+ Sexe pot)
                # On itère sur les ages, et pour chaque age on prend la col sexe
                for ak in age_keys:
                     section = details.get('age', {}).get(ak, {})
                     for sk in sex_keys:
                         val = section.get(sk, {}).get('milliers', 0)
                         total_audience += val
            
            # Filtre CSP (Intersection supplémentaire approx car pas de croisement Age x Sexe x CSP dispo)
            # Le JSON a Age x CSP+ (dans col 'foyers_csp_plus') OU Sexe x CSP+
            # Si CSP+ est coché, on applique un ratio.
            if criteria.get('csp'):
                 # Si "CSP+" demandé
                 if 'csp_plus' in criteria['csp']:
                     # On regarde le penetration CSP+ global du support
                     pen_csp = details['donnees_globales']['foyers_csp_plus']['structure'] / 100 # ex 0.25 (25% lecteurs sont csp+)
                     # C'est grossier. Mieux: Si Age selectionné, utiliser col 'foyers_csp_plus' de l'age
                     if age_keys:
                         # Recalcul avec col csp+
                         audience_csp = 0
                         for ak in age_keys:
                             val = details['age'][ak]['foyers_csp_plus']['milliers']
                             audience_csp += val
                         # Ici on remplace le total précédent par celui-ci ? 
                         # Si on a sélectionné 'Femmes' ET 'CSP+' ? Difficile.
                         # On va dire que CSP+ prime si présent pour l'estimation "Premium"
                         total_audience = audience_csp
                     else:
                         total_audience = details['donnees_globales']['foyers_csp_plus']['milliers']

            return total_audience * 1000 # En unités

        # === LOGIQUE POUR CORSE MATIN (audience.json) ===
        elif media_type == 'corse_matin':
            # Structure différente: pas de croisement direct Age x Sexe dans les chiffres
            # On a Total Age, et Total Sexe.
            # On assume indépendance: P(A inter B) = P(A) * P(B)
            
            # 1. Calcul Ratio Sexe
            ratio_sexe = 1.0
            if criteria.get('sexe'):
                # Somme des audiences des sexes sélectionnés
                aud_sexe = 0
                for s in criteria['sexe']:
                    # keys audience.json: 'homme', 'femme'
                    if s in details['sexe']:
                        aud_sexe += details['sexe'][s]['corse_matin_pondere']
                
                # Ratio = Audience Sexe / Audience Totale
                total_cm = details['donnees_principales']['cible_ensemble']['corse_matin_valeur']
                ratio_sexe = aud_sexe / total_cm if total_cm > 0 else 0
            
            # 2. Calcul Audience Age
            base_aud_age = details['donnees_principales']['cible_ensemble']['corse_matin_valeur']
            if criteria.get('age'):
                aud_age = 0
                # Mapping Frontend -> JSON CM
                mapping_age_cm = {
                    '15_24_ans': '15_24_ans',
                    '25_34_ans': '25_34_ans',
                    '35_49_ans': '35_49_ans',
                    '50_64_ans': '50_64_ans', 
                    '65_ans_ou_plus': '65_ans_ou_plus'
                }
                for a in criteria['age']:
                    if a in mapping_age_cm:
                        key = mapping_age_cm[a]
                        aud_age += details['age']['tranches'][key]['corse_matin_pondere']
                base_aud_age = aud_age
            
            # 3. Application CSP
            ratio_csp = 1.0
            if criteria.get('csp'):
                 # CM a une section pcs
                 aud_csp = 0
                 total_cm = details['donnees_principales']['cible_ensemble']['corse_matin_valeur']
                 
                 # Mapping approx
                 if 'csp_plus' in criteria['csp']:
                     aud_csp += details['pcs']['csp_plus']['corse_matin_pondere']
                 if 'actifs' in criteria['csp']:
                      aud_csp += details['age']['cibles']['actifs']['corse_matin_pondere']
                 if 'retraites' in criteria['csp']:
                      aud_csp += details['pcs']['categories']['retraites']['corse_matin_pondere']
                 
                 # Si selection multiple, attention aux doublons (Actifs contient CSP+)
                 # Simple max ou somme pondérée ? On prend le ratio du groupe le plus large ou somme si distincts
                 ratio_csp = aud_csp / total_cm if total_cm > 0 else 0

            # Résultat combiné
            final_audience = base_aud_age * ratio_sexe * ratio_csp
            return int(final_audience * 1000)

        return base_audience

    if items:
        # Mode PRÉCIS basé sur les items sélectionnés
        for item in items:
            qty = item.get('quantity', 1)
            item_type = item.get('type')
            item_id = item.get('format') # Id du format, ex: 'diverto_page', 'instagram'
            
            reach_unit = 0
            impressions_unit = 0
            
            if item_type == 'print':
                media_key = 'corse_matin'
                if 'diverto' in item_id: media_key = 'diverto'
                elif 'femina' in item_id: media_key = 'femina'
                
                # APPEL NOUVELLE FONCTION CIBLEE
                reach_unit = get_targeted_audience(media_key, target_criteria)
                impressions_unit = reach_unit # Print: 1 impression = 1 lecteur (approx)
                
            elif item_type == 'digital':
                # Pour le digital, on garde l'approche CPM mais on peut réduire le reach "utile"
                # si le ciblage est très restrictif (ex: on achète 100k imp mais sur cible Senior uniquement)
                # On utilise le coefficient d'affinité générique pour réduire le 'reach utile'
                
                impressions_unit = item.get('baseImpressions', 50000)
                
                # Calcul affinité (reprise code précédent simplifié)
                affinity = get_affinity_coefficient('digital', target_criteria)
                reach_unit = (impressions_unit / 3) * affinity
                
            elif item_type == 'social':
                network = 'Facebook' # Default
                if 'instagram' in item_id: network = 'Instagram'
                elif 'linkedin' in item_id: network = 'LinkedIn'
                
                followers = audience_data['social'].get(network, 50000)
                media_key = 'social' # Pas de json detaille pour social, on use affinity
                
                affinity = get_affinity_coefficient(media_key, target_criteria)
                
                reach_unit = (followers * 0.5) * affinity
                impressions_unit = reach_unit * 1.5
            
            estimated_reach += (reach_unit * qty)
            estimated_impressions += (impressions_unit * qty)
            
        # Déduplication simple
        estimated_reach = estimated_reach * 0.85
        
    else:
        # Mode ESTIMATION basé sur budget global (legacy / auto)
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
        
        for channel, channel_budget in budgets.items():
            if channel == 'events':
                # Event participants
                estimated_impressions += (channel_budget / cost_per_mille[channel]) * 10 # 1 participant = 10 "contacts" visuels/auditifs
            else:
                estimated_impressions += (channel_budget / cost_per_mille[channel]) * 1000
        
        # Reach estimé (unique)
        estimated_reach = estimated_impressions / 4  # Approximation: 4 impressions par personne sur mix media
        
    # Ajustement par mode cible (B2B audience plus faible)
    if target_mode == 'professionnels':
        estimated_reach *= 0.6 
        
    return {
        'estimated_reach': round(estimated_reach),
        'estimated_impressions': round(estimated_impressions),
        'estimated_participants': 0, # Calcul simplifié
        'estimated_cpm': round(budget / (estimated_impressions / 1000), 2) if estimated_impressions > 0 else 0,
        'estimated_cpc': round(budget / (estimated_reach * 0.05), 2) if estimated_reach > 0 else 0 # 5% CTR global
    }

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

# ==================== ROUTES MEDIA ====================

@media_bp.route('/options', methods=['GET'])
def get_media_options():
    """
    Retourne la liste des options/supports disponibles
    Sources: tarif_CMP.json, Diverto, Femina
    """
    try:
        options = get_available_options()
        return jsonify(options), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@media_bp.route('/plan', methods=['POST'])
def generate_media_plan():
    """
    Générer un plan média avec répartition intelligente
    Accepte le JSON au format des exemples (plat)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Données JSON requises"}), 400
        
        # Adaptation pour supporter les anciennes structures (wrapper) et les nouvelles (flat)
        campaign = data
        if "campaign_data" in data:
            campaign = data["campaign_data"]
            campaign_source = "wrapped_json"
        else:
            campaign_source = "direct_json"

        # Extraire les informations
        form_data = campaign.get('formData', {})
        if not form_data:
            return jsonify({"error": "Structure invalide : 'formData' manquant"}), 400

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
        # On regarde d'abord dans formData.repartition (cas manuel exemple)
        # Puis dans la racine (cas manuel backend ancien)
        # Sinon auto
        
        manual_repartition = form_data.get('repartition') or campaign.get('budget_allocation')
        repartition_mode = campaign.get('repartitionMode', 'auto')
        
        if repartition_mode == 'manuel' and manual_repartition:
            budget_allocation = manual_repartition
            allocation_mode = 'manuel'
            # Convertir les clés du json exemple qui sont parfois 'reseaux' au lieu de 'social' ?
            # Les exemples ont : "print", "digital", "reseaux", "event"
            # Le backend attend : "print", "digital", "social", "events"
            # Mapping
            mapping = {
                'reseaux': 'social',
                'event': 'events',
                'reseauxSociaux': 'social'
            }
            cleaned_allocation = {}
            for k, v in budget_allocation.items():
                new_key = mapping.get(k, k)
                cleaned_allocation[new_key] = v
            budget_allocation = cleaned_allocation
            
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
        # total_percentage = sum(budget_allocation.values())
        # if abs(total_percentage - 100) > 1:  # Tolérance de 1%
        #    # En mode manuel, on pourrait être strict, mais en auto, on a déjà normalisé.
        #    pass
        
        # Calculer les budgets par canal
        budgets = {
            channel: round((budget * float(percentage)) / 100, 2)
            for channel, percentage in budget_allocation.items()
        }
        
        # Suggérer des supports spécifiques
        suggested_supports = suggest_supports(budget_allocation, target, target_mode)
        
        # Récupérer les items si fournis (pour calcul précis)
        items = form_data.get('items')
        
        # Calculer les KPI cibles
        kpi_targets = calculate_kpi_targets(budget, budget_allocation, target, items)
        
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
                    "percentage": budget_allocation.get(channel, 0),
                    "recommended_supports": suggested_supports.get(channel, []),
                    "rationale": get_channel_rationale(channel, budget_allocation.get(channel, 0), target, target_mode)
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
            "campaign_source": campaign_source,
            "media_plan": media_plan
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Erreur: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500
