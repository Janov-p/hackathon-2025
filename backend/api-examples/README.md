# Documentation API - Plan Média Corse-Matin

Ce dossier contient les exemples de requêtes JSON pour l'API de génération de plan média.

## Fichiers

| Fichier | Description |
|---------|-------------|
| `request-particulier-manuel.json` | Cible particuliers avec répartition manuelle |
| `request-particulier-auto.json` | Cible particuliers avec répartition automatique par l'API |
| `request-professionnel-manuel.json` | Cible professionnels (B2B) avec répartition manuelle |
| `request-professionnel-auto.json` | Cible professionnels (B2B) avec répartition automatique par l'API |
| `response-example.json` | Exemple de réponse attendue de l'API |

## Modes de répartition

### Mode `manuel`
- Le client définit lui-même la répartition du budget entre les supports
- Le client sélectionne les supports qu'il souhaite utiliser
- Les champs `repartition`, `supportsPrint`, `supportsDigital`, `reseauxSociaux`, `events` sont remplis

### Mode `auto` (régie)
- L'API calcule la répartition optimale du budget
- L'API sélectionne les supports les plus pertinents
- Les champs `repartition`, `supportsPrint`, `supportsDigital`, `reseauxSociaux`, `events` sont vides ou absents
- L'API doit les remplir dans la réponse

## Cibles

## Champs communs

| Champ | Obligatoire | Description |
|-------|-------------|-------------|
| `zones` | Oui | Zones géographiques (Corse-du-Sud, Haute-Corse, ou les deux) |
| `microZones` | Non | Villes/communes spécifiques (facultatif si toute la zone est ciblée) |
| `objectifs` | Oui | Au moins un objectif |
| `budget` | Oui | Budget en euros |

### Particuliers (`targetMode: "particuliers"`)
Champs spécifiques :
- `ages` : Tranches d'âge ciblées
- `sexe` : "homme", "femme" ou "mixte"
- `csp` : Catégories socio-professionnelles
- `centresInteret` : Centres d'intérêt

### Professionnels (`targetMode: "professionnels"`)
Champs spécifiques :
- `taillesEntreprise` : TPE, PME, ETI, GE
- `secteursCibles` : Secteurs d'activité ciblés
- `fonctions` : Fonctions décisionnaires ciblées
- `zoneImplantation` : Zones d'implantation des entreprises cibles
