// Secteurs d'activité
export const SECTEURS = [
  { value: 'distribution', label: 'Distribution' },
  { value: 'automobile', label: 'Automobile' },
  { value: 'btp', label: 'BTP' },
  { value: 'sante', label: 'Santé' },
  { value: 'tourisme', label: 'Tourisme' },
  { value: 'institutionnel', label: 'Institutionnel' },
  { value: 'immobilier', label: 'Immobilier' },
  { value: 'restauration', label: 'Restauration' },
  { value: 'services', label: 'Services' },
  { value: 'autre', label: 'Autre' }
]

// Zones géographiques principales
export const ZONES_GEO = [
  { value: 'corse-du-sud', label: 'Corse-du-Sud' },
  { value: 'haute-corse', label: 'Haute-Corse' },
  { value: 'corse-entiere', label: 'Toute Corse' }
]

// Ciblage micro-territorial
export const MICRO_ZONES = [
  { value: 'ajaccio', label: 'Ajaccio' },
  { value: 'bastia', label: 'Bastia' },
  { value: 'balagne', label: 'Balagne' },
  { value: 'plaine-orientale', label: 'Plaine orientale' },
  { value: 'porto-vecchio', label: 'Porto-Vecchio' },
  { value: 'corte', label: 'Corte' },
  { value: 'sartenais', label: 'Sartenais' },
  { value: 'cap-corse', label: 'Cap Corse' }
]

// Objectifs de campagne
export const OBJECTIFS = [
  { value: 'notoriete', label: 'Notoriété', description: 'Faire connaître la marque/produit' },
  { value: 'image', label: 'Image/Branding', description: 'Améliorer la perception' },
  { value: 'drive-to-store', label: 'Drive-to-store', description: 'Trafic en magasin' },
  { value: 'trafic-web', label: 'Trafic web/e-commerce', description: 'Générer des visites en ligne' },
  { value: 'lancement', label: 'Lancement produit/événement', description: 'Promouvoir une nouveauté' },
  { value: 'fidelisation', label: 'Fidélisation/Engagement', description: 'Renforcer la relation client' }
]

// Cible Professionnels - Taille d'entreprise
export const TAILLES_ENTREPRISE = [
  { value: 'tpe', label: 'TPE' },
  { value: 'pme', label: 'PME' },
  { value: 'eti', label: 'ETI' },
  { value: 'grandes-entreprises', label: 'Grandes entreprises' }
]

// Cible Professionnels - Secteurs cibles
export const SECTEURS_CIBLES = [
  { value: 'commerce', label: 'Commerce' },
  { value: 'industrie', label: 'Industrie' },
  { value: 'services', label: 'Services' },
  { value: 'agriculture', label: 'Agriculture' },
  { value: 'tourisme', label: 'Tourisme' },
  { value: 'btp', label: 'BTP' }
]

// Cible Professionnels - Fonctions décisionnaires
export const FONCTIONS = [
  { value: 'dirigeants', label: 'Dirigeants' },
  { value: 'drh', label: 'DRH' },
  { value: 'directeurs-marketing', label: 'Directeurs marketing' },
  { value: 'daf', label: 'DAF' }
]

// Cible Particuliers - Tranches d'âge
export const TRANCHES_AGE = [
  { value: '15-24', label: '15-24 ans' },
  { value: '25-34', label: '25-34 ans' },
  { value: '35-49', label: '35-49 ans' },
  { value: '50-64', label: '50-64 ans' },
  { value: '65+', label: '65 ans et +' }
]

// Cible Particuliers - Sexe
export const SEXES = [
  { value: 'hommes', label: 'Hommes' },
  { value: 'femmes', label: 'Femmes' },
  { value: 'mixte', label: 'Mixte' }
]

// Cible Particuliers - CSP
export const CSP = [
  { value: 'csp+', label: 'CSP+' },
  { value: 'csp-', label: 'CSP-' },
  { value: 'actifs', label: 'Actifs' },
  { value: 'retraites', label: 'Retraités' },
  { value: 'etudiants', label: 'Étudiants' }
]

// Cible Particuliers - Centres d'intérêt
export const CENTRES_INTERET = [
  { value: 'consommation-locale', label: 'Consommation locale' },
  { value: 'immobilier', label: 'Immobilier' },
  { value: 'automobile', label: 'Automobile' },
  { value: 'sante', label: 'Santé' },
  { value: 'loisirs', label: 'Loisirs' },
  { value: 'culture', label: 'Culture' },
  { value: 'sport', label: 'Sport' }
]

// Supports Print
export const SUPPORTS_PRINT = {
  quotidien: [
    { value: 'quotidien-corse-matin', label: 'Quotidien Corse-Matin', tarif: 1500 }
  ],
  supplements: [
    { value: 'supplement-moteurs', label: 'Moteurs', tarif: 800 },
    { value: 'supplement-immo', label: 'Immo', tarif: 900 },
    { value: 'supplement-ecunumia', label: 'Ecunumia', tarif: 700 },
    { value: 'supplement-impiegu', label: 'Impiegu', tarif: 600 },
    { value: 'supplement-sante', label: 'Santé', tarif: 750 }
  ],
  magazines: [
    { value: 'magazine-diverto', label: 'Diverto', tarif: 1200 },
    { value: 'magazine-version-femina', label: 'Version Femina', tarif: 1100 },
    { value: 'magazine-hors-series', label: 'Hors-séries', tarif: 1000 }
  ]
}

// Supports Digital
export const SUPPORTS_DIGITAL = {
  sites: [
    { value: 'site-corsematin', label: 'Site CorseMatin.com', info: '2,5M visites/mois', tarif: 2000 },
    { value: 'app-corsematin', label: 'Application Corse-Matin', info: '400K visites/mois', tarif: 1500 }
  ],
  formats: [
    { value: 'format-habillage', label: 'Habillage', tarif: 3000 },
    { value: 'format-pave', label: 'Pavé', tarif: 500 },
    { value: 'format-demi-page', label: 'Demi-page', tarif: 800 },
    { value: 'format-interstitiel', label: 'Interstitiel appli', tarif: 1200 },
    { value: 'format-smart-cover', label: 'Smart cover mobile', tarif: 1500 },
    { value: 'format-preroll', label: 'Preroll vidéo', tarif: 2000 }
  ]
}

// Réseaux sociaux
export const RESEAUX_SOCIAUX = [
  { value: 'facebook', label: 'Facebook', tarif: 500 },
  { value: 'instagram', label: 'Instagram', tarif: 600 },
  { value: 'linkedin', label: 'LinkedIn', tarif: 800 },
  { value: 'youtube', label: 'YouTube', tarif: 1000 }
]

// Events
export const EVENTS = [
  { value: 'club-impresa', label: 'Club Impresa', tarif: 5000 },
  { value: 'parlons-sante', label: 'Parlons Santé', tarif: 4000 },
  { value: 'salons', label: 'Salons', tarif: 3000 },
  { value: 'trophees', label: 'Trophées', tarif: 6000 }
]

// Options de répartition budget
export const REPARTITION_OPTIONS = [
  { value: 'personnalisee', label: 'Répartition personnalisée' },
  { value: 'regie', label: 'Au choix de la régie' }
]

// Valeurs par défaut pour les sliders de répartition
export const DEFAULT_REPARTITION = {
  print: 40,
  digital: 35,
  reseaux: 15,
  event: 10
}

// Données de référence pour les calculs KPI
export const KPI_REFERENCE = {
  audienceBase: 185000, // Audience de base Corse
  tauxCouvertureBase: 0.68,
  frequenceMoyenne: 4.2,
  cpmBase: 19.20,
  ctrMoyen: 0.015,
  tauxVueVideo: 0.65
}
