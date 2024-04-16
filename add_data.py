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
    return weaviate.connect_to_local()

def delete_existing(collection_name, client: WeaviateClient) -> bool:
    client.collections.delete(collection_name)
    return True

DATA_LIMITER = 5


def demo_query(client: WeaviateClient):

    # print("-"*100)
    # print(" "*45 + "Images")
    # print("-"*100)

    # img_collection = client.collections.get('images')

    # response = img_collection.aggregate.over_all(total_count=True)
    # print(f"Object count in the Database: {response.total_count}")

    # for q in ["lions", "a big crowd", "happy students"]:
    #     response = img_collection.query.near_text(q, limit=3)
    #     print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
    #     print(f"\t\t {q} \n")
    #     print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
    #     for r in response.objects:
    #         print(r.properties["filename"])

    # print("-"*100)
    # print(" "*45 + "Wine Reviews")
    # print("-"*100)

    # wine_reviws_collection = client.collections.get('WineReviews')

    # response = wine_reviws_collection.aggregate.over_all(total_count=True)
    # print(f"Object count in the Database: {response.total_count}")

    # for q in ["tart wine"]:
    #     response = wine_reviws_collection.query.near_text(q, limit=3)
    #     print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
    #     print(f"\t\t {q} \n")
    #     print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
    #     for r in response.objects:
    #         # print(r)
    #         print(r.properties["filename"])
            

    # print("-"*100)
    # print(" "*45 + "PDF Files")
    # print("-"*100)

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
    
    # Images
    from create_collections.Images import define_collection_images,import_data_images
    delete_existing('images',client)
    define_collection_images(client)
    import_data_images(client)

    # Wines -- csv
    from create_collections.Wines import define_collection_wine_reviews, import_data_wine_reviews
    delete_existing('WineReviews',client)
    define_collection_wine_reviews(client)
    import_data_wine_reviews(client)

    # Pdfs
    from create_collections.PDF import define_collection_pdfs,import_data_pdf
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
