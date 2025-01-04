from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
import sys

def test_blob_storage_connection():
    # Load environment variables
    load_dotenv()
    connection_string = os.getenv("BLOB_CONNECTION_STRING")

    if not connection_string:
        print("Error: BLOB_CONNECTION_STRING is not set in the environment variables or .env file.")
        sys.exit(1)

    try:
        # Initialize BlobServiceClient
        print("Connecting to Azure Blob Storage...")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # List all containers in the storage account
        print("Connection successful! Listing containers:")
        containers = blob_service_client.list_containers()
        for container in containers:
            print(f"- {container['name']}")

        print("\nConnection test completed successfully!")

    except Exception as e:
        print(f"Error: Unable to connect to Azure Blob Storage. Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_blob_storage_connection()
