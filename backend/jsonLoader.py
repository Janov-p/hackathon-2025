import json

def loader(filePath:str)->dict:
    """Charge un fichier JSON et rend ces données sous la forme d'un dictionnaire de dictionnaires

    Args:
        filePath (str): Chemin d'accès du fichier

    Returns:
        dict: Dictionnaire avec l'ensemble des données du JSON
    """
    try:
        with open(filePath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except:
        print("Erreur, impossible d'ouvrir le fichier")
        return {}

def collect_subdicts_with_paths(obj):
    """
    Parcours récursif d'un objet (dict/list/tuple) et retourne
    une liste de tuples (path, subdict) où `path` est la liste des
    clés/indices parents menant au sous-dictionnaire.

    Exemples de `path`: [] (pour l'objet racine), ['a'] (sous-dict
    sous la clé 'a'), ['a', 0, 'b'] (sous-dict trouvé dans une liste
    indexée à 0 sous la clé 'a', puis sous la clé 'b').
    """
    results = []

    def _collect(o, path):
        if isinstance(o, dict):
            results.append((list(path), o))
            for k, v in o.items():
                _collect(v, path + [k])
        elif isinstance(o, (list, tuple)):
            for idx, item in enumerate(o):
                _collect(item, path + [idx])

    _collect(obj, [])
    return results

def collectData(data:list, search:str) -> dict:
    """Permet de trier les données collecté

    Args:
        data (list): Données sous la forme d'une liste de tuple où le premier argument est le chemin d'accès dans le json et le second est un dictionnaire des données collecté 
        search (str): Dictionnaire recherché

    Returns:
        dict: Dictionnaire de données recherché, ou dict vide si non trouvé
    """
    for i in data:
        if i[0] != [] and i[0][-1] == search:
            return i[1]
    return {}  # Retourne un dict vide si rien n'est trouvé
        
def getDataPathNames(data:list):
    """Permet d'obtenir l'ensemble des champs de recherche possible dans les données collecté

    Args:
        data (list): Données sous la forme d'une liste de tuple où le premier argument est le chemin d'accès dans le json et le second est un dictionnaire des données collecté 

    Returns:
        list: Ensemble des champs de recherche disponible
    """
    return [i[0][-1] for i in data if i[0] != []]

def simplification(json: str, choice: str = ""):
    """Simplifie l'accès aux données JSON collectées
    
    Args:
        json (str): Chemin du fichier JSON
        choice (str): Clé spécifique à rechercher. Si vide, retourne la liste complète.
    
    Returns:
        dict | list: Dict si choice fourni, sinon liste de tuples (path, dict)
    """
    data = collect_subdicts_with_paths(loader(json))
    if choice:
        return collectData(data, choice)
    return data


def get_subdicts_by_key(json: str, key: str) -> dict:
    """Récupère un sous-dictionnaire par sa clé (wrapper typé pour simplification)
    
    Args:
        json (str): Chemin du fichier JSON
        key (str): Clé du sous-dictionnaire recherchée
    
    Returns:
        dict: Dictionnaire trouvé ou vide
    """
    result = simplification(json, key)
    return result if isinstance(result, dict) else {}

def extractDataOneNext(lst:dict, fstArg:str="", sndArg:str="", trdArg:str=""):
    """summary

    Args:
        lst (list): fichier json
        fstArg (str): premierArgument
        sndArg (str): 2ndArgument

    Returns:
        type: Something
    """
    if trdArg != "":
        return lst[fstArg][sndArg][trdArg]
    return lst[fstArg][sndArg]

#print(extractDataOneNext(get_subdicts_by_key("backend/testfiles/VF_OneNext.json", "femme"), "ensemble", "penetration"))
print(collectData(collect_subdicts_with_paths(loader("backend/testfiles/chiffre_cles.json")),"Visites Totales"))
#print(getDataPathNames(collect_subdicts_with_paths(loader("backend/testfiles/VF_OneNext.json"))))