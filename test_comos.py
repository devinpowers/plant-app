import os
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
load_dotenv()

# Test Configuration
CONNECTION_STRING = os.getenv("COSMOS_DB_CONNECTION_STRING")
DATABASE_NAME = "plant_database"  # Replace with your database name
CONTAINER_NAME = "plant_container"  # Replace with your container name

# Get the Cosmos DB connection string
connection_string = os.getenv("COSMOS_DB_CONNECTION_STRING")

if connection_string:
    print("[INFO] Cosmos DB connection string loaded.")
else:
    print("[ERROR] COSMOS_DB_CONNECTION_STRING is not set.")

# Test script
if not CONNECTION_STRING:
    print("[ERROR] COSMOS_DB_CONNECTION_STRING environment variable is not set.")
    exit(1)

def test_cosmos_connection():
    try:
        print("[INFO] Testing Cosmos DB connection...")
        cosmos_client = CosmosClient.from_connection_string(CONNECTION_STRING)
        print("[SUCCESS] Connection to Cosmos DB client successful.")

        print("[INFO] Testing access to database...")
        database = cosmos_client.get_database_client(DATABASE_NAME)
        print(f"[SUCCESS] Accessed database '{DATABASE_NAME}'.")

        print("[INFO] Testing access to container...")
        container = database.get_container_client(CONTAINER_NAME)
        print(f"[SUCCESS] Accessed container '{CONTAINER_NAME}'.")

        print("[INFO] Testing container query...")
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        print(f"[SUCCESS] Queried container. Retrieved {len(items)} items.")

    except exceptions.CosmosHttpResponseError as e:
        print(f"[ERROR] Cosmos DB HTTP error: {e.message}")
    except exceptions.CosmosResourceNotFoundError:
        print("[ERROR] Database or container not found.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    test_cosmos_connection()
