import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { DEFAULT_REPARTITION } from '../data/constants'

export const useCampaignStore = defineStore('campaign', () => {
  // Mode cible (professionnels ou particuliers) - null by default, user must choose
  const targetMode = ref(null)

  // Données du formulaire
  const formData = ref({
    // Section 1: Informations générales
    nomClient: '',
    matriculeCommercial: '',
    nom: '',
    secteur: '',
    periodeDebut: '',
    periodeFin: '',
    zones: [],
    microZones: [],
    
    // Informations entreprise (depuis API recherche-entreprises)
    entreprise: {
      siren: '',
      siret: '',
      nomComplet: '',
      nomRaisonSociale: '',
      sigle: '',
      adresse: '',
      codePostal: '',
      commune: '',
      departement: '',
      activitePrincipale: '',
      categorieEntreprise: '', // TPE, PME, ETI, GE
      natureJuridique: '',
      dateCreation: '',
      dirigeants: []
    },

    // Section 2: Objectifs
    objectifs: [],

    // Section 3: Cible Professionnels
    taillesEntreprise: [],
    secteursCibles: [],
    fonctions: [],
    zoneImplantation: [],

    // Section 3: Cible Particuliers
    ages: [],
    sexe: 'mixte',
    csp: [],
    centresInteret: [],

    // Section 4: Budget
    budget: 10000,
    repartitionMode: 'regie',
    repartition: { ...DEFAULT_REPARTITION },

    // Section 5: Supports
    supportsPrint: [],
    supportsDigital: [],
    reseauxSociaux: [],
    events: []
  })

  // Résultats KPI
  const kpiResults = ref({
    audienceCumulee: 0,
    tauxCouverture: 0,
    frequenceMoyenne: 0,
    grp: 0,
    impressions: 0,
    vuesVideo: 0,
    coutGrp: 0,
    cpmGlobal: 0,
    clicsEstimes: 0,
    ctrMoyen: 0,
    budgetParSupport: {
      print: 0,
      digital: 0,
      reseaux: 0,
      event: 0
    }
  })

  // Plan média
  const mediaPlan = ref({
    supportsRecommandes: [],
    formatsProposés: [],
    calendrier: [],
    chiffrage: {
      totalHT: 0,
      parSupport: {},
      parSemaine: []
    }
  })

  // États
  const isLoading = ref(false)
  const lastUpdate = ref(null)

  // Mode édition du plan média
  const isEditingPlan = ref(false)
  const modifiedPlan = ref(null)
  const remise = ref({
    active: false,
    type: 'pourcentage', // ou 'montant'
    valeur: 0,
    visible: true // afficher sur le PDF ou non
  })

  // Computed: vérifier si le formulaire est suffisamment rempli (tous les champs obligatoires)
  const isComplete = computed(() => {
    // Section 1: Informations générales (tous obligatoires)
    const hasBasicInfo = formData.value.nom && 
                         formData.value.secteur && 
                         formData.value.zones.length > 0
    
    // Section 2: Objectifs (au moins un)
    const hasObjectifs = formData.value.objectifs.length > 0
    
    // Section 3: Cible (tous les champs obligatoires selon le mode)
    let hasTarget = false
    if (targetMode.value === 'professionnels') {
      // Pro: taille ET secteurs obligatoires
      hasTarget = formData.value.taillesEntreprise.length > 0 && 
                  formData.value.secteursCibles.length > 0
    } else {
      // Particuliers: âge ET CSP obligatoires
      hasTarget = formData.value.ages.length > 0 && 
                  formData.value.csp.length > 0
    }
    
    // Section 4: Budget (obligatoire)
    const hasBudget = formData.value.budget > 0

    return hasBasicInfo && hasObjectifs && hasTarget && hasBudget
  })

  // Computed: progression du formulaire (0-100)
  const formProgress = computed(() => {
    let progress = 0
    const steps = 5

    // Section 1: Infos générales (20%)
    if (formData.value.nom) progress += 4
    if (formData.value.secteur) progress += 4
    if (formData.value.periodeDebut && formData.value.periodeFin) progress += 6
    if (formData.value.zones.length > 0) progress += 6

    // Section 2: Objectifs (20%)
    if (formData.value.objectifs.length > 0) progress += 20

    // Section 3: Cible (20%)
    if (targetMode.value === 'professionnels') {
      if (formData.value.taillesEntreprise.length > 0) progress += 7
      if (formData.value.secteursCibles.length > 0) progress += 7
      if (formData.value.fonctions.length > 0) progress += 6
    } else {
      if (formData.value.ages.length > 0) progress += 7
      if (formData.value.sexe) progress += 3
      if (formData.value.csp.length > 0) progress += 7
      if (formData.value.centresInteret.length > 0) progress += 3
    }

    // Section 4: Budget (20%)
    if (formData.value.budget > 0) progress += 20

    // Section 5: Supports (20% bonus)
    const hasSupports = formData.value.supportsPrint.length > 0 ||
      formData.value.supportsDigital.length > 0 ||
      formData.value.reseauxSociaux.length > 0 ||
      formData.value.events.length > 0
    if (hasSupports) progress += 20

    return Math.min(progress, 100)
  })

  // Computed: budget final après remise
  const budgetFinal = computed(() => {
    const baseBudget = modifiedPlan.value?.budget?.initial || formData.value.budget
    if (!remise.value.active) return baseBudget
    if (remise.value.type === 'pourcentage') {
      return Math.round(baseBudget * (1 - remise.value.valeur / 100))
    }
    return Math.max(0, baseBudget - remise.value.valeur)
  })

  // Actions
  function updateField(field, value) {
    if (field.includes('.')) {
      const [parent, child] = field.split('.')
      formData.value[parent][child] = value
    } else {
      formData.value[field] = value
    }
  }

  function setTargetMode(mode) {
    targetMode.value = mode
  }

  function updateRepartition(key, value) {
    const oldValue = formData.value.repartition[key]
    const diff = value - oldValue
    
    // Ajuster les autres valeurs proportionnellement
    const otherKeys = Object.keys(formData.value.repartition).filter(k => k !== key)
    const otherTotal = otherKeys.reduce((sum, k) => sum + formData.value.repartition[k], 0)
    
    if (otherTotal > 0) {
      otherKeys.forEach(k => {
        const proportion = formData.value.repartition[k] / otherTotal
        formData.value.repartition[k] = Math.max(0, Math.round(formData.value.repartition[k] - diff * proportion))
      })
    }
    
    formData.value.repartition[key] = value
    
    // Normaliser pour que le total soit 100
    const total = Object.values(formData.value.repartition).reduce((a, b) => a + b, 0)
    if (total !== 100) {
      const adjustment = 100 - total
      const maxKey = otherKeys.reduce((a, b) => 
        formData.value.repartition[a] > formData.value.repartition[b] ? a : b
      )
      formData.value.repartition[maxKey] += adjustment
    }
  }

  async function generateResults() {
    if (!isComplete.value) return

    isLoading.value = true

    // Simuler un délai API
    await new Promise(resolve => setTimeout(resolve, 300))

    const budget = formData.value.budget
    const zonesCount = formData.value.zones.length
    const objectifsCount = formData.value.objectifs.length

    // Facteurs de calcul basés sur les inputs
    const zoneFactor = zonesCount === 3 ? 1 : zonesCount === 2 ? 0.7 : 0.4
    const objectifFactor = 1 + (objectifsCount * 0.1)
    const budgetFactor = budget / 10000

    // Calcul des KPI (placeholder avec variations)
    const baseAudience = 125000
    kpiResults.value = {
      audienceCumulee: Math.round(baseAudience * zoneFactor * objectifFactor),
      tauxCouverture: Math.round(68 * zoneFactor * 10) / 10,
      frequenceMoyenne: Math.round((4.2 + budgetFactor * 0.5) * 10) / 10,
      grp: Math.round(285.6 * budgetFactor * zoneFactor * 10) / 10,
      impressions: Math.round(520000 * budgetFactor * zoneFactor),
      vuesVideo: Math.round(45000 * budgetFactor),
      coutGrp: Math.round(35 / budgetFactor),
      cpmGlobal: Math.round(19.20 * (1 / budgetFactor) * 100) / 100,
      clicsEstimes: Math.round(7800 * budgetFactor),
      ctrMoyen: 1.5,
      budgetParSupport: {
        print: Math.round(budget * formData.value.repartition.print / 100),
        digital: Math.round(budget * formData.value.repartition.digital / 100),
        reseaux: Math.round(budget * formData.value.repartition.reseaux / 100),
        event: Math.round(budget * formData.value.repartition.event / 100)
      }
    }

    // Génération du plan média
    const supportsRecommandes = []
    
    if (formData.value.repartition.print > 0) {
      supportsRecommandes.push({
        type: 'Print',
        nom: 'Quotidien Corse-Matin',
        justification: 'Couverture régionale optimale, forte crédibilité'
      })
    }
    if (formData.value.repartition.digital > 0) {
      supportsRecommandes.push({
        type: 'Digital',
        nom: 'Site CorseMatin.com',
        justification: '2,5M visites/mois, ciblage précis'
      })
    }
    if (formData.value.repartition.reseaux > 0) {
      supportsRecommandes.push({
        type: 'Réseaux sociaux',
        nom: 'Facebook + Instagram',
        justification: 'Engagement fort, viralité potentielle'
      })
    }
    if (formData.value.repartition.event > 0) {
      supportsRecommandes.push({
        type: 'Event',
        nom: 'Club Impresa',
        justification: 'Networking B2B, visibilité premium'
      })
    }

    // Formats proposés
    const formatsProposés = [
      { support: 'Quotidien', format: '1/4 page', dimensions: '130x180mm', tarifUnitaire: 850, quantite: 4, total: 3400 },
      { support: 'Site web', format: 'Pavé', dimensions: '300x250px', tarifUnitaire: 500, quantite: Math.ceil(budget / 5000), total: 500 * Math.ceil(budget / 5000) },
      { support: 'Facebook', format: 'Carrousel', dimensions: '1080x1080px', tarifUnitaire: 200, quantite: 5, total: 1000 },
      { support: 'Instagram', format: 'Story', dimensions: '1080x1920px', tarifUnitaire: 150, quantite: 8, total: 1200 }
    ]

    // Calendrier (semaines)
    const nbSemaines = 4
    const calendrier = []
    for (let i = 1; i <= nbSemaines; i++) {
      calendrier.push({
        semaine: i,
        actions: [
          { support: 'Print', action: i === 1 ? 'Lancement' : 'Rappel' },
          { support: 'Digital', action: 'Diffusion continue' },
          { support: 'RS', action: i % 2 === 1 ? 'Post sponsorisé' : 'Story' }
        ]
      })
    }

    mediaPlan.value = {
      supportsRecommandes,
      formatsProposés,
      calendrier,
      chiffrage: {
        totalHT: budget,
        parSupport: kpiResults.value.budgetParSupport,
        parSemaine: Array(nbSemaines).fill(0).map((_, i) => ({
          semaine: i + 1,
          montant: Math.round(budget / nbSemaines)
        }))
      }
    }

    lastUpdate.value = new Date()
    isLoading.value = false
  }

  function resetForm() {
    targetMode.value = null
    formData.value = {
      nomClient: '',
      matriculeCommercial: '',
      nom: '',
      secteur: '',
      periodeDebut: '',
      periodeFin: '',
      zones: [],
      microZones: [],
      entreprise: {
        siren: '',
        siret: '',
        nomComplet: '',
        nomRaisonSociale: '',
        sigle: '',
        adresse: '',
        codePostal: '',
        commune: '',
        departement: '',
        activitePrincipale: '',
        categorieEntreprise: '',
        natureJuridique: '',
        dateCreation: '',
        dirigeants: []
      },
      objectifs: [],
      taillesEntreprise: [],
      secteursCibles: [],
      fonctions: [],
      zoneImplantation: [],
      ages: [],
      sexe: 'mixte',
      csp: [],
      centresInteret: [],
      budget: 10000,
      repartitionMode: 'regie',
      repartition: { ...DEFAULT_REPARTITION },
      supportsPrint: [],
      supportsDigital: [],
      reseauxSociaux: [],
      events: []
    }
    
    kpiResults.value = {
      audienceCumulee: 0,
      tauxCouverture: 0,
      frequenceMoyenne: 0,
      grp: 0,
      impressions: 0,
      vuesVideo: 0,
      coutGrp: 0,
      cpmGlobal: 0,
      clicsEstimes: 0,
      ctrMoyen: 0,
      budgetParSupport: { print: 0, digital: 0, reseaux: 0, event: 0 }
    }
    
    mediaPlan.value = {
      supportsRecommandes: [],
      formatsProposés: [],
      calendrier: [],
      chiffrage: { totalHT: 0, parSupport: {}, parSemaine: [] }
    }
    
    lastUpdate.value = null
    
    // Reset edit mode
    isEditingPlan.value = false
    modifiedPlan.value = null
    remise.value = {
      active: false,
      type: 'pourcentage',
      valeur: 0,
      visible: true
    }
  }

  // Edit mode functions
  function enterEditMode() {
    isEditingPlan.value = true
    // Deep clone the current media plan
    modifiedPlan.value = {
      budget: {
        initial: formData.value.budget,
        remise: { ...remise.value },
        final: budgetFinal.value
      },
      repartition: { ...formData.value.repartition },
      supports: {
        print: [...formData.value.supportsPrint],
        digital: [...formData.value.supportsDigital],
        reseauxSociaux: [...formData.value.reseauxSociaux],
        events: [...formData.value.events]
      },
      formatsProposés: JSON.parse(JSON.stringify(mediaPlan.value.formatsProposés)),
      calendrier: JSON.parse(JSON.stringify(mediaPlan.value.calendrier)),
      supportsRecommandes: JSON.parse(JSON.stringify(mediaPlan.value.supportsRecommandes))
    }
  }

  function exitEditMode(save = false) {
    if (save && modifiedPlan.value) {
      // Apply changes to formData
      formData.value.budget = modifiedPlan.value.budget.initial
      formData.value.repartition = { ...modifiedPlan.value.repartition }
      formData.value.supportsPrint = [...modifiedPlan.value.supports.print]
      formData.value.supportsDigital = [...modifiedPlan.value.supports.digital]
      formData.value.reseauxSociaux = [...modifiedPlan.value.supports.reseauxSociaux]
      formData.value.events = [...modifiedPlan.value.supports.events]
      
      // Apply changes to mediaPlan
      mediaPlan.value.formatsProposés = modifiedPlan.value.formatsProposés
      mediaPlan.value.calendrier = modifiedPlan.value.calendrier
      mediaPlan.value.supportsRecommandes = modifiedPlan.value.supportsRecommandes
      
      // Update chiffrage
      const totalHT = modifiedPlan.value.formatsProposés.reduce((sum, f) => sum + f.total, 0)
      mediaPlan.value.chiffrage.totalHT = totalHT
    }
    
    isEditingPlan.value = false
    modifiedPlan.value = null
  }

  function updateModifiedPlan(path, value) {
    if (!modifiedPlan.value) return
    
    const keys = path.split('.')
    let obj = modifiedPlan.value
    for (let i = 0; i < keys.length - 1; i++) {
      obj = obj[keys[i]]
    }
    obj[keys[keys.length - 1]] = value
  }

  function updateRemise(field, value) {
    remise.value[field] = value
    if (modifiedPlan.value) {
      modifiedPlan.value.budget.remise = { ...remise.value }
      modifiedPlan.value.budget.final = budgetFinal.value
    }
  }

  async function recalculateKpis() {
    if (!modifiedPlan.value) return
    
    isLoading.value = true
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Recalculate based on modified plan
    const budget = budgetFinal.value
    const zonesCount = formData.value.zones.length
    const objectifsCount = formData.value.objectifs.length
    const rep = modifiedPlan.value.repartition

    const zoneFactor = zonesCount === 3 ? 1 : zonesCount === 2 ? 0.7 : 0.4
    const objectifFactor = 1 + (objectifsCount * 0.1)
    const budgetFactor = budget / 10000

    const baseAudience = 125000
    kpiResults.value = {
      audienceCumulee: Math.round(baseAudience * zoneFactor * objectifFactor),
      tauxCouverture: Math.round(68 * zoneFactor * 10) / 10,
      frequenceMoyenne: Math.round((4.2 + budgetFactor * 0.5) * 10) / 10,
      grp: Math.round(285.6 * budgetFactor * zoneFactor * 10) / 10,
      impressions: Math.round(520000 * budgetFactor * zoneFactor),
      vuesVideo: Math.round(45000 * budgetFactor),
      coutGrp: Math.round(35 / Math.max(budgetFactor, 0.1)),
      cpmGlobal: Math.round(19.20 * (1 / Math.max(budgetFactor, 0.1)) * 100) / 100,
      clicsEstimes: Math.round(7800 * budgetFactor),
      ctrMoyen: 1.5,
      budgetParSupport: {
        print: Math.round(budget * rep.print / 100),
        digital: Math.round(budget * rep.digital / 100),
        reseaux: Math.round(budget * rep.reseaux / 100),
        event: Math.round(budget * rep.event / 100)
      }
    }

    // Update chiffrage in modified plan
    const totalHT = modifiedPlan.value.formatsProposés.reduce((sum, f) => sum + f.total, 0)
    modifiedPlan.value.chiffrage = {
      totalHT: totalHT || budget,
      parSupport: kpiResults.value.budgetParSupport,
      parSemaine: modifiedPlan.value.calendrier.map((s, i) => ({
        semaine: s.semaine,
        montant: Math.round((totalHT || budget) / modifiedPlan.value.calendrier.length)
      }))
    }

    lastUpdate.value = new Date()
    isLoading.value = false
  }

  return {
    // State
    targetMode,
    formData,
    kpiResults,
    mediaPlan,
    isLoading,
    lastUpdate,
    isEditingPlan,
    modifiedPlan,
    remise,
    
    // Computed
    isComplete,
    formProgress,
    budgetFinal,
    
    // Actions
    updateField,
    setTargetMode,
    updateRepartition,
    generateResults,
    resetForm,
    enterEditMode,
    exitEditMode,
    updateModifiedPlan,
    updateRemise,
    recalculateKpis
  }
})
