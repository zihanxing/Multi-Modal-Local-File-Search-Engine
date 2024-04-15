import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path

import json

# COLLECTION_NAME = "MultiModalCollection"
imgdir = Path("data/images")


def connect() -> WeaviateClient:
    return weaviate.connect_to_local()

def delete_existing(collection_name, client: WeaviateClient) -> bool:
    client.collections.delete(collection_name)
    return True




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

def import_data_podcasts(client: WeaviateClient, podcast_dir: Path) -> BatchObjectReturn:
    podcast_coll = client.collections.get('podcasts')

    data_objs = list()
    for f in podcast_dir.glob("*.json"):  # assuming podcast data is in JSON files
        # podcast_data = json.loads(f.read_text())
        with open(f, 'r', encoding='utf-8') as file:
           podcast_data = json.load(file)
        for podcast in podcast_data:
            data_props = {
                "title": podcast["title"],
                "transcript": podcast["transcript"],
                # "description": podcast["description"],
                # "titleimage": base64.b64encode(Path(podcast["titleimage"]).read_bytes()).decode(),
            }
            data_obj = wvc.data.DataObject(
                properties=data_props, uuid=generate_uuid5(f.name)
            )
            data_objs.append(data_obj)

    insert_response = podcast_coll.data.insert_many(data_objs)

    print(f"{len(insert_response.all_responses)} insertions complete.")
    print(f"{len(insert_response.errors)} errors within.")
    if insert_response.has_errors:
        for e in insert_response.errors:
            print(e)

    return insert_response

    


def demo_query(client: WeaviateClient):

    mm_coll = client.collections.get('images')

    response = mm_coll.aggregate.over_all(total_count=True)
    print(f"Object count: {response.total_count}")

    for q in ["lions", "a big crowd", "happy students"]:
        response = mm_coll.query.near_text(q, limit=3)
        print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
        print(f"\t\t {q} \n")
        print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
        for r in response.objects:
            print(r.properties["filename"])

    print()
    print()
    print()
    print()
    print()
    print()
    print()


    mm_coll = client.collections.get('podcasts')

    response = mm_coll.aggregate.over_all(total_count=True)
    print(f"Object count: {response.total_count}")

    for q in ["lions", "a big crowd", "happy students"]:
        response = mm_coll.query.near_text(q, limit=3)
        print(f"\n{'*'*10} \t Query: \t {'*'*10}\n")
        print(f"\t\t {q} \n")
        print(f"{'*'*10} \t RESULTS: \t {'*'*10}\n")
        for r in response.objects:
            print(r.properties["filename"])


    return True




def define_collection_images(client: WeaviateClient, collection_name: str = 'images') -> bool:
    client.collections.create(
        name=collection_name,
        description="Image collection",
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
            image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
            # text_fields=[wvc.config.Multi2VecField(name='filedesc', weight=0.05)],
            vectorize_collection_name=False 
        ),
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

# def define_collection_imsasages(client: WeaviateClient) -> bool:
#     client.collections.create(
#         name=COLLECTION_NAME,
#         vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
#             image_fields=["image"],
#             vectorize_collection_name=False,
#         ),
#         generative_config=wvc.config.Configure.Generative.openai(),
#         properties=[
#             wvc.Property(
#                 name="image",
#                 data_type=wvc.config.DataType.BLOB,
#             ),
#             wvc.Property(
#                 name="filename",
#                 data_type=wvc.config.DataType.TEXT,
#                 skip_vectorization=True,  # Not vectorizing for demonstrative purposes
#             ),
#         ],
#     )
#     return True

def define_collection_podcasts(client: WeaviateClient, collection_name: str = 'podcasts') -> bool:
    client.collections.create(
        name=collection_name,
        description='Collection of podcasts and their transcripts',
        # vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
        #     # fields=[
        #     #     wvc.config.Multi2VecField(name='title', weight=0.85),
        #     #     wvc.config.Multi2VecField(name='transcript', weight=0.05),
        #     #     wvc.config.Multi2VecField(name='description', weight=0.05),
        #     #     wvc.config.Multi2VecField(name='titleimage', weight=0.05)
        #     # ],
        #     # image_fields=[wvc.config.Multi2VecField(name='title', weight=0.95)],
        #     text_fields=[wvc.config.Multi2VecField(name='description', weight=0.05)],
        #     vectorize_collection_name=False,
        # ),
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_transformers(),
        generative_config=wvc.config.Configure.Generative.openai(),
        properties=[
            wvc.Property(
                name="title",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=False,
            ),
            wvc.Property(
                name="transcript",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=False,
            ),
            wvc.Property(
                name="description",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=False,
            ),
            wvc.Property(
                name="titleimage",
                data_type=wvc.config.DataType.BLOB,
                skip_vectorization=False,
            ),
        ],
    )
    return True



def main():
    client = connect()
    # delete_existing(client)

    # Images
    # from collections import Images
    delete_existing('images',client)
    define_collection_images(client)
    import_data_images(client)

    # Podcasts
    # from collections.Podcasts import define_collection_podcasts, import_data_podcasts
    delete_existing('podcasts',client)
    define_collection_podcasts(client)
    import_data_podcasts(client, Path("data/podcasts"))  # replace with your actual podcast data directory


    # #Text
    # define_collection_text(client,'text')


    # #Audios
    # define_collection_audio(client,'audio')


    # #PDF
    # define_collection_pdf(client,'pdf')

    
    demo_query(client)


if __name__ == "__main__":
    main()
