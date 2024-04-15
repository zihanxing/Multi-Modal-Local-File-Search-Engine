import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path

# def define_collection_podcasts(client: WeaviateClient, collection_name: str = 'podcasts') -> bool:
    
#     client.collections.create(
#         name=collection_name,
#         description='Collection of podcasts and their transcripts',

#         vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
#             title_fields=[wvc.config.Multi2VecField(name='title', weight=0.85)],
#             transcript_fields=[wvc.config.Multi2VecField(name='transcript', weight=0.05)],
#             decription_fields=[wvc.config.Multi2VecField(name='description', weight=0.05)],
#             titleimage_fields=[wvc.config.Multi2VecField(name='titleimage', weight=0.05)],
#             vectorize_collection_name=False,
#         ),

#             # wvc.ConfigFactory.Vectorizer.text2vec_transformers()


#         generative_config=wvc.config.Configure.Generative.openai(),
#         properties=[
#             wvc.Property(
#                 name="title",
#                 data_type=wvc.config.DataType.TEXT,
#             ),
#             wvc.Property(
#                 name="transcript",
#                 data_type=wvc.config.DataType.TEXT,
#                 skip_vectorization=True,  # Not vectorizing for demonstrative purposes
#             ),
#             wvc.Property(
#                 name="description",
#                 data_type=wvc.config.DataType.TEXT,
#                 skip_vectorization=True,  # Not vectorizing for demonstrative purposes
#             ),
#             wvc.Property(
#                 name="titleimage",
#                 data_type=wvc.config.DataType.BLOB,
#                 skip_vectorization=True,  # Not vectorizing for demonstrative purposes
#             ), # add audio as well?, # add the tone, # people in the podcast, # description
#         ],
#     )
#     return True


#chatgpt corrected func
def define_collection_podcasts(client: WeaviateClient, collection_name: str = 'podcasts') -> bool:
    client.collections.create(
        name=collection_name,
        description='Collection of podcasts and their transcripts',
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
            fields=[
                wvc.config.Multi2VecField(name='title', weight=0.85),
                wvc.config.Multi2VecField(name='transcript', weight=0.05),
                wvc.config.Multi2VecField(name='description', weight=0.05),
                wvc.config.Multi2VecField(name='titleimage', weight=0.05)
            ],
            vectorize_collection_name=False,
        ),
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
