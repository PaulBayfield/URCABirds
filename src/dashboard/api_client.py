import os
from dotenv import load_dotenv
import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from requests.exceptions import RequestException

# Client HTTP qui encapsule tous les appels vers l'API REST URCABirds
class APIClient:
    def __init__(self, base_url: str):
        """Initialise le client avec l'URL de base de l'API.

        Args:
            base_url: URL racine de l'API (ex. ``http://localhost:8000``).
                Le slash final est supprimé pour éviter les doubles slashes.
        """
        self.base_url = base_url.rstrip('/')

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Effectue une requête GET sur l'API et retourne le champ ``data`` en cas de succès.

        Args:
            endpoint: Chemin relatif à ``/v1`` (ex. ``/detections``).
            params: Paramètres de requête à passer dans l'URL (query string).

        Returns:
            Le contenu du champ ``data`` de la réponse JSON si ``success`` est ``True``,
            ``None`` sinon (erreur métier ou erreur réseau).
        """
        url = f"{self.base_url}/v1{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Lève une exception si code HTTP >= 400
            data = response.json()
            if data.get("success"):
                return data.get("data")
            else:
                # L'API a répondu mais signale une erreur métier
                st.error(f"API Error: {data.get('message', 'Unknown error')}")
                return None
        except RequestException as e:
            # Erreur réseau ou serveur injoignable
            st.error(f"Failed to connect to API at {url}: {str(e)}")
            return None

    def get_detections(self, limit: int = 50, offset: int = 0, species: str = None, sensor_id: str = None) -> Dict[str, Any]:
        """Récupère une page de détections avec filtres optionnels.

        Args:
            limit: Nombre maximum de détections à retourner (défaut : 50).
            offset: Décalage de pagination (défaut : 0).
            species: Filtre sur le nom scientifique de l'espèce (correspondance exacte).
            sensor_id: Filtre sur l'identifiant du capteur.

        Returns:
            Dictionnaire avec les clés :

            - ``detections`` (list) : liste des détections.
            - ``total`` (int) : nombre total de résultats côté serveur (avant pagination).

            Retourne ``{"detections": [], "total": 0}`` si l'API est injoignable.
        """
        params = {"limit": limit, "offset": offset}
        if species:
            params["species"] = species
        if sensor_id:
            params["sensor_id"] = sensor_id

        return self._get("/detections", params=params) or {"detections": [], "total": 0}

    def get_sensors(self) -> List[Dict[str, Any]]:
        """Récupère la liste de tous les capteurs enregistrés.

        Returns:
            Liste de dictionnaires décrivant chaque capteur (``sensor_id``, ``name``,
            ``latitude``, ``longitude``, ``total_detections``, etc.).
            Retourne une liste vide si l'API est injoignable.
        """
        return self._get("/sensors") or []

    def get_species(self) -> List[Dict[str, Any]]:
        """Récupère la liste de toutes les espèces détectées.

        Returns:
            Liste de dictionnaires décrivant chaque espèce (``name``,
            ``total_detections``, ``last_detection``, etc.).
            Retourne une liste vide si l'API est injoignable.
        """
        return self._get("/species") or []


# Chargement des variables d'environnement (.env) puis instanciation du client global
load_dotenv()
api_url = os.environ.get("API_URL", "http://localhost:8000")
client = APIClient(api_url)
