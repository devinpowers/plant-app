from azure.cosmos import CosmosClient
import  os

DATABASE_NAME = 'plant_database'
CONTAINER_NAME = 'plant_container'

connection_string = os.getenv("COSMOS_DB_CONNECTION_STRING")


def clear_data():
    try:
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)

        # Query all items in the container
        items = list(container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))

        # Delete each item
        for item in items:
            container.delete_item(item=item['id'], partition_key=item['id'])
            print(f"Deleted item with ID: {item['id']}")

        print("All items have been cleared.")
    except Exception as e:
        print(f"Error clearing data: {e}")

if __name__ == "__main__":
    clear_data()
