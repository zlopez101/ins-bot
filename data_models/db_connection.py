from typing import List, Union
import azure.cosmos.documents as documents
from azure.cosmos.cosmos_client import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import ContainerProxy, DatabaseProxy
from .models import cpt_code, insurance_exception

import datetime

import config


class AzureDB:
    """Holds methods and container attributes for the bot
    """

    def __init__(self):
        self.HOST = config.settings["host"]
        self.MASTER_KEY = config.settings["master_key"]
        self.DATABASE_ID = config.settings["database_id"]
        self.client = client = CosmosClient(self.HOST, {"masterKey": self.MASTER_KEY})
        self.db: DatabaseProxy = client.get_database_client(self.DATABASE_ID)
        self.cpt_codes: ContainerProxy = self.db.get_container_client("cpt_codes")
        self.cpt_exceptions_by_insurance: ContainerProxy = self.db.get_container_client(
            "cpt_exceptions_by_insurance"
        )

    def read_item(self, container, doc_id, account_number):
        print("\nReading Item by Id\n")

        # We can do an efficient point read lookup on partition key and id
        response = container.read_item(item=doc_id, partition_key=account_number)

        print("Item read by Id {0}".format(doc_id))
        print("Partition Key: {0}".format(response.get("partitionKey")))
        print("Subtotal: {0}".format(response.get("subtotal")))

    def read_items(self, container):
        print("\nReading all items in a container\n")

        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        item_list = list(self, container.read_all_items(max_item_count=10))

        print("Found {0} items".format(item_list.__len__()))

        for doc in item_list:
            print("Item Id: {0}".format(doc.get("id")))

    def create_item(self, container: str, item: dict) -> None:
        """Create the item in the specified container. Item requires an id variable. /pk should be required?

        Args:
            container (str): container id to create in
            item (dict): item to insert into the DB
        """
        assert item.get("id"), "ID is a required property"
        db_container: ContainerProxy = getattr(self, container)
        db_container.create_item(body=item)

    def query_cpt_code(self, id: Union[str, int] = None) -> List[cpt_code]:
        """get the specified cpt code from the database, or query for all items

        Args:
            id (Union[str, int], optional): id to query. Defaults to None.

        Returns:
            List[cpt_code]: cpt_code results
        """
        if id:
            return [
                cpt_code.from_db(item)
                for item in self.cpt_codes.query_items(
                    query="SELECT * FROM cpt_codes WHERE cpt_codes.id=@id",
                    parameters=[{"name": "@id", "value": id}],
                    enable_cross_partition_query=True,
                )
            ]
        else:  # if none specified, get all the items
            return [
                cpt_code.from_db(item)
                for item in self.cpt_codes.query_items(
                    query="SELECT * FROM cpt_codes ", enable_cross_partition_query=True,
                )
            ]

    def query_cpt_exceptions_by_insurance(
        self, id: Union[str, int] = None
    ) -> List[insurance_exception]:
        """get the specified cpt_code exceptions by insurance

        Args:
            id (Union[str, int], optional): Id of insurance to query. Defaults to None.

        Returns:
            List[insurance_exception]: insurance exception results
        """
        if id:
            return [
                insurance_exception.from_db(item)
                for item in self.cpt_exceptions_by_insurance.query_items(
                    query="SELECT * FROM r WHERE r.id=@id",
                    parameters=[{"name": "@id", "value": id}],
                    enable_cross_partition_query=True,
                )
            ]
        else:
            return [
                insurance_exception.from_db(item)
                for item in self.cpt_exceptions_by_insurance.query_items(
                    query="SELECT * FROM r ", enable_cross_partition_query=True,
                )
            ]

    def upsert_item(self, container, doc_id, account_number):
        """TBD

        Args:
            container ([type]): [description]
            doc_id ([type]): [description]
            account_number ([type]): [description]
        """
        print("\nUpserting an item\n")

        read_item = container.read_item(item=doc_id, partition_key=account_number)
        read_item["subtotal"] = read_item["subtotal"] + 1
        response = container.upsert_item(body=read_item)

        print(
            "Upserted Item's Id is {0}, new subtotal={1}".format(
                response["id"], response["subtotal"]
            )
        )

    def delete_item(self, container, doc_id, account_number):
        print("\nDeleting Item by Id\n")

        response = container.delete_item(item=doc_id, partition_key=account_number)

        print("Deleted item's Id is {0}".format(doc_id))


if __name__ == "__main__":
    pass

