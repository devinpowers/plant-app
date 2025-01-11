from flask import Flask
from .main import get_cosmos_container, blob_service_client

app = Flask(__name__)

# Attach services to the app
app.get_cosmos_container = get_cosmos_container
app.blob_service_client = blob_service_client

# Expose the app object
__all__ = ["app"]

