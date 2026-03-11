import logging
import aiohttp

from .db import Database
from aiohttp import ClientSession


class APIClient:
    """
    API Client, handles requests to the API
    """

    def __init__(
        self, session: ClientSession, base_url: str, api_key: str, sensor_id: str
    ) -> None:
        """
        Initialises the APIClient with the provided session, base URL, API key, and sensor ID.

        :param session: The session to use for making requests.
        :type session: ClientSession
        :param base_url: The base URL of the API.
        :type base_url: str
        :param api_key: The API key to use for authentication.
        :type api_key: str
        :param sensor_id: The ID of the sensor to use for the detections.
        :type sensor_id: str
        """
        self.base_url = base_url
        self.api_key = api_key
        self.sensor_id = sensor_id
        self.session = session
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    async def register_sensor(
        self,
        name: str,
        latitude: float,
        longitude: float,
        description: str | None = None,
    ) -> bool:
        """
        Registers (or updates) this sensor via POST /v1/sensors/register.
        Updates last_connection on every call; sets first_registered on first call.

        :param name: Human-readable name of the sensor.
        :type name: str
        :param latitude: Latitude of the sensor.
        :type latitude: float
        :param longitude: Longitude of the sensor.
        :type longitude: float
        :param description: Optional description.
        :type description: str | None
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        payload = {
            "sensor_id": self.sensor_id,
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
        }
        if description:
            payload["description"] = description

        try:
            async with self.session.post(
                f"{self.base_url}/sensors/register", json=payload, timeout=10.0
            ) as response:
                if response.status in (200, 201):
                    action = "registered" if response.status == 201 else "updated"
                    logging.info(f"Sensor '{self.sensor_id}' {action} successfully.")
                    return True
                else:
                    text = await response.text()
                    logging.warning(
                        f"Sensor registration returned {response.status}: {text}"
                    )
                    return False
        except aiohttp.ClientError as e:
            logging.warning(f"Sensor registration failed: {e}")
            return False

    async def send_detection(
        self, detection: dict, database: Database, record_id=None
    ) -> bool:
        """
        Sends the detection data to the server via POST to /detections.
        Applies the timeout of 5 seconds.

        :param detection: The detection data to send.
        :type detection: dict
        :param record_id: The ID of the record to use for the detections.
        :type record_id: str
        :return: True if the detection was successfully sent, False otherwise.
        :rtype: bool
        """
        payload = {
            "sensor_id": self.sensor_id,
            "timestamp": detection["timestamp"],
            "species": detection["species"],
            "confidence": detection["confidence"],
        }

        try:
            async with self.session.post(
                f"{self.base_url}/detections", json=payload, timeout=5.0
            ) as response:
                response.raise_for_status()

                # Update cache if it was successfully synced just now
                if record_id is not None:
                    database.mark_synced(record_id)
                    logging.info(f"Successfully synced cached record: {record_id}")

                return True

        except aiohttp.ClientError as e:
            logging.warning(f"Detection send failed: {e}. Will cache for later sync.")
            return False
