import { ref } from 'vue'

/**
 * Composable pour rechercher des entreprises via l'API recherche-entreprises.api.gouv.fr
 * Documentation: https://recherche-entreprises.api.gouv.fr/docs/
 */
export function useEntrepriseSearch() {
  const results = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const selectedEntreprise = ref(null)

  const API_BASE = 'https://recherche-entreprises.api.gouv.fr'

  /**
   * Recherche des entreprises par nom, SIREN ou SIRET
   * @param {string} query - Terme de recherche
   * @param {object} options - Options de recherche
   */
  async function searchEntreprises(query, options = {}) {
    if (!query || query.length < 2) {
      results.value = []
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const params = new URLSearchParams({
        q: query,
        page: options.page || 1,
        per_page: options.perPage || 10,
        // Filtrer uniquement les entreprises actives
        etat_administratif: 'A'
      })

      // Filtres optionnels
      if (options.codePostal) {
        params.append('code_postal', options.codePostal)
      }
      if (options.departement) {
        params.append('departement', options.departement)
      }
      if (options.region) {
        params.append('region', options.region)
      }
      if (options.activitePrincipale) {
        params.append('activite_principale', options.activitePrincipale)
      }

      const response = await fetch(`${API_BASE}/search?${params}`)
      
      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
      }

      const data = await response.json()
      
      // Transformer les résultats pour extraire les infos pertinentes
      results.value = data.results.map(entreprise => formatEntreprise(entreprise))
      
      return results.value
    } catch (err) {
      error.value = err.message
      results.value = []
      console.error('Erreur recherche entreprise:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Recherche une entreprise par son SIRET exact
   * @param {string} siret - Numéro SIRET (14 chiffres)
   */
  async function getEntrepriseBySiret(siret) {
    if (!siret || siret.length !== 14) {
      error.value = 'SIRET invalide (14 chiffres requis)'
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/search?q=${siret}&mtm_campaign=hackathon`)
      
      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.results && data.results.length > 0) {
        // Trouver l'entreprise avec le SIRET exact
        const entreprise = data.results.find(e => 
          e.siege?.siret === siret || 
          e.matching_etablissements?.some(etab => etab.siret === siret)
        )
        
        if (entreprise) {
          selectedEntreprise.value = formatEntreprise(entreprise)
          return selectedEntreprise.value
        }
      }
      
      error.value = 'Entreprise non trouvée'
      return null
    } catch (err) {
      error.value = err.message
      console.error('Erreur recherche SIRET:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Recherche une entreprise par son SIREN
   * @param {string} siren - Numéro SIREN (9 chiffres)
   */
  async function getEntrepriseBySiren(siren) {
    if (!siren || siren.length !== 9) {
      error.value = 'SIREN invalide (9 chiffres requis)'
      return null
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/search?q=${siren}`)
      
      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.results && data.results.length > 0) {
        const entreprise = data.results.find(e => e.siren === siren)
        
        if (entreprise) {
          selectedEntreprise.value = formatEntreprise(entreprise)
          return selectedEntreprise.value
        }
      }
      
      error.value = 'Entreprise non trouvée'
      return null
    } catch (err) {
      error.value = err.message
      console.error('Erreur recherche SIREN:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Formate les données d'une entreprise pour l'affichage
   */
  function formatEntreprise(entreprise) {
    const siege = entreprise.siege || {}
    
    return {
      // Identifiants
      siren: entreprise.siren,
      siret: siege.siret,
      
      // Dénomination
      nomComplet: entreprise.nom_complet,
      nomRaisonSociale: entreprise.nom_raison_sociale,
      sigle: entreprise.sigle,
      nomCommercial: siege.nom_commercial,
      
      // Adresse du siège
      adresse: {
        complete: siege.adresse || siege.geo_adresse,
        numeroVoie: siege.numero_voie,
        typeVoie: siege.type_voie,
        libelleVoie: siege.libelle_voie,
        codePostal: siege.code_postal,
        commune: siege.libelle_commune,
        departement: siege.departement,
        region: siege.region,
        coordonnees: {
          latitude: siege.latitude,
          longitude: siege.longitude
        }
      },
      
      // Activité
      activitePrincipale: siege.activite_principale,
      sectionActivite: entreprise.section_activite_principale,
      
      // Informations juridiques
      natureJuridique: entreprise.nature_juridique,
      categorieEntreprise: entreprise.categorie_entreprise, // TPE, PME, ETI, GE
      
      // Effectifs
      trancheEffectif: siege.tranche_effectif_salarie,
      caractereEmployeur: siege.caractere_employeur === 'O',
      
      // Dates
      dateCreation: entreprise.date_creation,
      dateDebutActivite: siege.date_debut_activite,
      
      // État
      etatAdministratif: entreprise.etat_administratif, // A = Actif, F = Fermé
      estActif: entreprise.etat_administratif === 'A',
      
      // Dirigeants (si disponibles)
      dirigeants: (entreprise.dirigeants || []).map(d => ({
        nom: d.nom,
        prenoms: d.prenoms,
        qualite: d.qualite,
        type: d.type_dirigeant
      })),
      
      // Compléments
      estAssociation: entreprise.complements?.est_association || false,
      estESS: entreprise.complements?.est_ess || false,
      estEntrepreneurIndividuel: entreprise.complements?.est_entrepreneur_individuel || false,
      
      // Nombre d'établissements
      nombreEtablissements: entreprise.nombre_etablissements,
      nombreEtablissementsOuverts: entreprise.nombre_etablissements_ouverts,
      
      // Données brutes pour référence
      _raw: entreprise
    }
  }

  /**
   * Sélectionne une entreprise parmi les résultats
   */
  function selectEntreprise(entreprise) {
    selectedEntreprise.value = entreprise
    return entreprise
  }

  /**
   * Réinitialise la recherche
   */
  function clearSearch() {
    results.value = []
    error.value = null
    selectedEntreprise.value = null
  }

  /**
   * Formate un SIRET pour l'affichage (xxx xxx xxx xxxxx)
   */
  function formatSiret(siret) {
    if (!siret) return ''
    const clean = siret.replace(/\s/g, '')
    return `${clean.slice(0, 3)} ${clean.slice(3, 6)} ${clean.slice(6, 9)} ${clean.slice(9)}`
  }

  /**
   * Formate un SIREN pour l'affichage (xxx xxx xxx)
   */
  function formatSiren(siren) {
    if (!siren) return ''
    const clean = siren.replace(/\s/g, '')
    return `${clean.slice(0, 3)} ${clean.slice(3, 6)} ${clean.slice(6)}`
  }

  return {
    // State
    results,
    isLoading,
    error,
    selectedEntreprise,
    
    // Actions
    searchEntreprises,
    getEntrepriseBySiret,
    getEntrepriseBySiren,
    selectEntreprise,
    clearSearch,
    
    // Helpers
    formatSiret,
    formatSiren
  }
}
