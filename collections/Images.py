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
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
            image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
            text_fields=[wvc.config.Multi2VecField(name='filedesc', weight=0.05)],
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
            wvc.Property(
                name="filedesc",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,  # Not vectorizing for demonstrative purposes
            ),
        ],
    )
    return True