import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path
import pandas as pd
import json

# COLLECTION_NAME = "MultiModalCollection"
imgdir = Path("data/images")


def connect() -> WeaviateClient:
    return weaviate.connect_to_local()

def delete_existing(collection_name, client: WeaviateClient) -> bool:
    client.collections.delete(collection_name)
    return True

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
    




# PDFs
def define_collection_pdfs(client: WeaviateClient, collection_name: str = 'pdfs') -> bool:

    # Creating a new collection with the defined schema
    client.collections.create(
        name=collection_name,
        properties=[
            wvc.Property(
                name="filename",
                data_type=wvc.DataType.TEXT,
            ),
            wvc.Property(
                name="abstract",
                data_type=wvc.DataType.TEXT,
            )
        ],
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            text_fields=[wvc.config.Multi2VecField(name='filename', weight=0.95)],
            vectorize_collection_name=False )
    )

def import_data_pdf(client: WeaviateClient,  collection_name: str = 'pdf') -> BatchObjectReturn:
    
    from unstructured.partition.pdf import partition_pdf
    from AbstractExtractor import AbstractExtractor

    data_folder = "data/pdf/"

    data_objects = []

    for path in Path(data_folder).iterdir():
        if path.suffix != ".pdf":
            continue

        print(f"Processing {path.name}...")

        elements = partition_pdf(filename=path)

        abstract_extractor = AbstractExtractor()
        abstract_extractor.consume_elements(elements)

        data_object = {"filename": path.name, "abstract": abstract_extractor.abstract()}

        data_objects.append(data_object)



    pdf_collection = client.collections.get('pdf')
    insert_response =pdf_collection.data.insert_many(data_objects)


    print(f"{len(insert_response.all_responses)} insertions complete.")
    print(f"{len(insert_response.errors)} errors within.")
    if insert_response.has_errors:
        for e in insert_response.errors:
            print(e)

    return insert_response




# Images
def import_data_images(client: WeaviateClient,  collection_name: str = 'images') -> BatchObjectReturn:
    mm_coll = client.collections.get(collection_name)

    data_objs = list()

    for f in imgdir.glob("*.jpg"):
        b64img = base64.b64encode(f.read_bytes()).decode()
        data_props = {"image": b64img, "filename": f.name}
        data_obj = wvc.data.DataObject(
            properties=data_props, uuid=generate_uuid5(f.name)
        )
        data_objs.append(data_obj)

    insert_response = mm_coll.data.insert_many(data_objs)

    print(f"{len(insert_response.all_responses)} insertions complete.")
    print(f"{len(insert_response.errors)} errors within.")
    if insert_response.has_errors:
        for e in insert_response.errors:
            print(e)

    return insert_response

def define_collection_images(client: WeaviateClient, collection_name: str = 'images') -> bool:
    client.collections.create(
        name=collection_name,
        description="Image collection",
        # vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
        #     image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
        #     # text_fields=[wvc.config.Multi2VecField(name='filedesc', weight=0.05)],
        #     vectorize_collection_name=False 
        # ),
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
            # text_fields=[wvc.config.Multi2VecField(name='filedesc', weight=0.05)],
            vectorize_collection_name=False ),


        generative_config=wvc.config.Configure.Generative.openai(),
        properties=[
            wvc.Property(
                name="image",
                data_type=wvc.config.DataType.BLOB,
            ),
            wvc.Property(
                name="filename",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,  # Not vectorizing for demonstrative purposes
            ),
            # wvc.Property(
            #     name="filedesc",
            #     data_type=wvc.config.DataType.TEXT,
            #     skip_vectorization=True,  # Not vectorizing for demonstrative purposes
            # ),
        ],
    )
    return True





def demo_query(client: WeaviateClient):

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

    wine_reviws_collection = client.collections.get('WineReviews')

    response = wine_reviws_collection.aggregate.over_all(total_count=True)
    print(f"Object count in the Database: {response.total_count}")

    for q in ["tart wine"]:
        response = wine_reviws_collection.query.near_text(q, limit=3)
        print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
        print(f"\t\t {q} \n")
        print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
        for r in response.objects:
            # print(r)
            print(r.properties["filename"])
            

    print("-"*100)
    print(" "*45 + "PDF Files")
    print("-"*100)

    pdf_collection = client.collections.get('pdf')

    response = pdf_collection.aggregate.over_all(total_count=True)
    print(f"Object count in the Database: {response.total_count}")

    for q in ["home prices"]:
        response = pdf_collection.query.hybrid(q, limit=3)
        print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
        print(f"\t\t {q} \n")
        print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
        for r in response.objects:
            # print(r)
            print(r.properties["filename"])
            

    return True




def main():
    client = connect()
    # delete_existing(client)

    # Images
    delete_existing('images',client)
    define_collection_images(client)
    import_data_images(client)

    # Wines -- csv
    delete_existing('WineReviews',client)
    define_collection_wine_reviews(client)
    import_data_wine_reviews(client)

    # Pdf
    delete_existing('pdf',client)
    define_collection_pdfs(client,'pdf')
    import_data_pdf(client)



    # Podcasts
    # # from collections.Podcasts import define_collection_podcasts, import_data_podcasts
    # delete_existing('podcasts',client)
    # define_collection_podcasts(client)
    # import_data_podcasts(client, Path("data/podcasts"))  # replace with your actual podcast data directory


    # #Text
    # define_collection_text(client,'text')


    # #Audios
    # define_collection_audio(client,'audio')


    # #PDF
    # define_collection_pdf(client,'pdf')

    
    demo_query(client)


if __name__ == "__main__":
    main()
