import os
from dotenv import load_dotenv
import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from requests.exceptions import RequestException

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Helper method to make GET requests to the API."""
        url = f"{self.base_url}/v1{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                return data.get("data")
            else:
                st.error(f"API Error: {data.get('message', 'Unknown error')}")
                return None
        except RequestException as e:
            st.error(f"Failed to connect to API at {url}: {str(e)}")
            return None

    def get_detections(self, limit: int = 50, offset: int = 0, species: str = None, sensor_id: str = None) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if species:
            params["species"] = species
        if sensor_id:
            params["sensor_id"] = sensor_id
            
        return self._get("/detections/", params=params) or {"detections": [], "total": 0}

    def get_sensors(self) -> List[Dict[str, Any]]:
        return self._get("/sensors/") or []
        
    def get_species(self) -> List[Dict[str, Any]]:
        return self._get("/species/") or []

# Initialize client
load_dotenv()
api_url = os.environ.get("API_URL", "http://localhost:8000")
client = APIClient(api_url)
