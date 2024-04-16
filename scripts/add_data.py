# Import necessary libraries
import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path
import pandas as pd
import json

def connect() -> WeaviateClient:
    """
    Connect to the local Weaviate instance.

    Returns:
        WeaviateClient: The connected Weaviate client.
    """
    return weaviate.connect_to_local()

def delete_existing(collection_name, client: WeaviateClient) -> bool:
    """
    Delete an existing collection in Weaviate.

    Args:
        collection_name (str): The name of the collection to delete.
        client (WeaviateClient): The Weaviate client.

    Returns:
        bool: True if deletion is successful, otherwise False.
    """
    client.collections.delete(collection_name)
    return True

# Set data limiter and demo query options
DATA_LIMITER = 5
VIDEOS = True
PDFS = True
IMAGES = True
CSVS = True

DEMO_QUERY_PDF = True
DEMO_QUERY_IMAGES = False
DEMO_QUERY_VIDEOS = False
DEMO_QUERY_CSV = False

def demo_query(client: WeaviateClient):
    """
    Perform a demo query on the Weaviate client.

    Args:
        client (WeaviateClient): The Weaviate client.
    """
    if DEMO_QUERY_IMAGES:
        # Demo query for images
        print("-"*100)
        print(" "*45 + "Images")
        print("-"*100)

        img_collection = client.collections.get('images')

        response = img_collection.aggregate.over_all(total_count=True)
        print(f"Object count in the Database: {response.total_count}")

        for q in ["lions", "a big crowd", "happy students"]:
            response = img_collection.query.near_text(q, limit=3)
            print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
            print(f"\t\t {q} \n")
            print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
            for r in response.objects:
                print(r.properties["filename"])

        print("-"*100)
        print(" "*45 + "Wine Reviews")
        print("-"*100)

    if DEMO_QUERY_CSV:
        # Demo query for CSV files
        wine_reviws_collection = client.collections.get('WineReviews')

        response = wine_reviws_collection.aggregate.over_all(total_count=True)
        print(f"Object count in the Database: {response.total_count}")

        for q in ["tart wine"]:
            response = wine_reviws_collection.query.near_text(q, limit=3)
            print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
            print(f"\t\t {q} \n")
            print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
            for r in response.objects:
                print(r.properties["filename"])

        print("-"*100)
        print(" "*45 + "PDF Files")
        print("-"*100)

    if DEMO_QUERY_PDF:
        # Demo query for PDF files
        pdf_collection = client.collections.get('pdf')

        response = pdf_collection.aggregate.over_all(total_count=True)
        print(f"Object count in the Database: {response.total_count}")

        for q in ["home prices"]:
            response = pdf_collection.query.hybrid(q, limit=3)
            print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
            print(f"\t\t {q} \n")
            print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
            for r in response.objects:
                print(r.properties["filename"])

    return True

def main():
    # Connect to Weaviate
    client = connect()

    # Define and import collections, and perform demo queries based on user preferences
    print('-'*100)
    print("Ingesting Images")
    print('-'*100)
    if IMAGES:
        # Images
        from create_collections.Images import define_collection_images, import_data_images
        delete_existing('images', client)
        define_collection_images(client)
        import_data_images(client)

    print('-'*100)
    print("Ingesting CSVs")
    print('-'*100)
    if CSVS:
        # Wines -- csv
        from create_collections.Wines import define_collection_wine_reviews, import_data_wine_reviews
        delete_existing('WineReviews', client)
        define_collection_wine_reviews(client)
        import_data_wine_reviews(client)

    print('-'*100)
    print("Ingesting PDFs")
    print('-'*100)
    if PDFS:
        # Pdfs
        from create_collections.PDF import define_collection_pdfs, import_data_pdf
        delete_existing('pdf', client)
        define_collection_pdfs(client, 'pdf')
        import_data_pdf(client)

    print('-'*100)
    print("Ingesting Videos")
    print('-'*100)
    if VIDEOS:
        # Videos
        from create_collections.Videos import define_collection_videos, import_data_videos
        delete_existing('videos', client)
        define_collection_videos(client, 'videos')
        import_data_videos(client)

    # Perform demo query
    demo_query(client)

if __name__ == "__main__":
    main()
