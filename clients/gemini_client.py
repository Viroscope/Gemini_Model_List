import os
import requests


class GeminiApiError(Exception):
    pass

class GeminiClient:
    """
    Client for interacting with the Gemini Models API.
    API key is retrieved from environment or provided explicitly.
    """
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise GeminiApiError('API key not provided')
        self.base_url = base_url or 'https://api.gemini.example.com'

    def fetch_models(self):
        """
        Fetch the list of models from the Gemini API.
        Returns a dict parsed from JSON response.
        """
        url = f"{self.base_url}/models"
        headers = {'Authorization': f'Bearer {self.api_key}'}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            raise GeminiApiError(f'Error fetching models: {e}')
        try:
            return resp.json()
        except ValueError:
            raise GeminiApiError('Invalid JSON response')