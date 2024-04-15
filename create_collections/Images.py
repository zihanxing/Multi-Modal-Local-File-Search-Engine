import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path

def define_collection_images(client: WeaviateClient, collection_name: str = 'images') -> bool:
    client.collections.create(
        name=collection_name,
        description="Image collection",
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
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
        ],
    )
    return True

def import_data_images(client: WeaviateClient,  collection_name: str = 'images') -> BatchObjectReturn:
    mm_coll = client.collections.get(collection_name)
    imgdir = Path("data/images")
    
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

# def define_collection_images(client: WeaviateClient, collection_name: str = 'images') -> bool:
#     client.collections.create(
#         name=collection_name,
#         description="Image collection",
#         vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
#             image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
#             text_fields=[wvc.config.Multi2VecField(name='filedesc', weight=0.05)],
#             vectorize_collection_name=False
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
#             wvc.Property(
#                 name="filedesc",
#                 data_type=wvc.config.DataType.TEXT,
#                 skip_vectorization=True,  # Not vectorizing for demonstrative purposes
#             ),
#         ],
#     )
#     return True