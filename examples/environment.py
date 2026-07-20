"""Read a token from the environment with a development fallback."""

from secrets_storage import ENVStorage, Secrets

secrets = Secrets([ENVStorage()])
api_token = secrets.get("API_TOKEN", fallback_value="development-token")
print(api_token)
