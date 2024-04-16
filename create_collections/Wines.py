import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path
import pandas as pd
import json

DATA_LIMITER = 5

# Wines_test
def define_collection_wine_reviews(client: WeaviateClient, collection_name: str = 'WineReviews') -> bool:

    # Creating a new collection with the defined schema
    client.collections.create(
        name=collection_name,
        properties=[
            wvc.Property(
                name="filename",
                data_type=wvc.DataType.TEXT,
            ),
            wvc.Property(
                name="description",
                data_type=wvc.DataType.TEXT,
            )
        ],
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            text_fields=[wvc.config.Multi2VecField(name='filename', weight=0.95)],
            vectorize_collection_name=False )
    )

def import_data_wine_reviews(client: WeaviateClient,  collection_name: str = 'WineReviews') -> BatchObjectReturn:

    data = pd.read_csv('./data/wine_reviews.csv', index_col=0)[:DATA_LIMITER]
    wine_collection = client.collections.get("WineReviews")

    wines_to_add = [
    wvc.DataObject(
            properties={
                "filename": row["title"] + '.',
                "description": row["description"],
            },
        )
        for index, row in data.iterrows()
    ]
    # Insertine the data into the collection
    response = wine_collection.data.insert_many(wines_to_add)

    # # Fetching any 2 wine reviews from the collection and printing the response
    # response = wine_collection.query.fetch_objects(limit=2)
    # print(response)

    print(f"{len(response.all_responses)} insertions complete.")
    print(f"{len(response.errors)} errors within.")
    if response.has_errors:
        for e in response.errors:
            print(e)

    return response
    

