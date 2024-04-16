from datetime import datetime, timezone
from pathlib import Path
import base64
from weaviate import WeaviateClient
from weaviate.util import generate_uuid5
import weaviate.classes as wvc
from weaviate.collections.classes.batch import BatchObjectReturn
from scripts.get_metadata import createFileRecords

def define_collection_videos(client: WeaviateClient, collection_name: str = 'videos') -> bool:
    # Define video collection
    client.collections.create(
        name=collection_name,
        description="Video collection",
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            video_fields=[wvc.config.Multi2VecField(name='video', weight=0.95)],
            text_fields=[wvc.config.Multi2VecField(name='filename', weight=0.05)],
            vectorize_collection_name=False
        ),
        generative_config=wvc.config.Configure.Generative.openai(),
        properties=[
            wvc.Property(
                name="video",
                data_type=wvc.config.DataType.BLOB,
            ),
            wvc.Property(
                name="filename",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,  # Not vectorizing for demonstrative purposes
            ),
            wvc.Property(
                name="date_created",
                data_type=wvc.config.DataType.DATE,
            ),
            wvc.Property(
                name="date_modified",
                data_type=wvc.config.DataType.DATE,
            ),
            wvc.Property(
                name="file_size",
                data_type=wvc.config.DataType.TEXT,
            ),
            wvc.Property(
                name="author",
                data_type=wvc.config.DataType.TEXT,
            ),
        ],
    )
    return True

def import_data_videos(client: WeaviateClient, collection_name: str = 'videos') -> BatchObjectReturn:
    # Get collection
    videos_coll = client.collections.get(collection_name)

    # Path to videos directory
    videos_dir = Path("data/videos")
    
    data_objs = []

    client.batch.configure(batch_size=1)  # Configure batch
    with client.batch as batch:
        # Iterate over video files
        for video_file in videos_dir.glob("*.mp4"):
            # Read video file as bytes and encode it in base64
            b64video = base64.b64encode(video_file.read_bytes()).decode()

            # Get metadata for the video file
            meta_data = createFileRecords(video_file)

            # Convert Creation Date and Modified Date to RFC 3339 format
            creation_date_rfc3339 = meta_data['Creation Date'].astimezone(timezone.utc).isoformat()
            modified_date_rfc3339 = meta_data['Modified Date'].astimezone(timezone.utc).isoformat()

            # Define data properties
            data_props = {
                "video": b64video, 
                "filename": video_file.name,
                "date_created": creation_date_rfc3339,
                "date_modified": modified_date_rfc3339,
                "file_size": meta_data['Size (KB)'],
                "author": '0'  # Set author as placeholder value
            }

            # Create data object
            # batch.add_data_object(data_props, "videos")
            a = batch.add_object(collection='videos',properties=data_props, uuid=generate_uuid5(video_file.name))
            # print('-'*100)
            # print(a)


# def import_data_videos(client: WeaviateClient, collection_name: str = 'videos') -> BatchObjectReturn:
#     # Get collection
#     videos_coll = client.collections.get(collection_name)

#     # Path to videos directory
#     videos_dir = Path("data/videos")
    
#     data_objs = []

#     # Iterate over video files
#     for video_file in videos_dir.glob("*.mp4"):
#         # Read video file as bytes and encode it in base64
#         b64video = base64.b64encode(video_file.read_bytes()).decode()

#         # Get metadata for the video file
#         meta_data = createFileRecords(video_file)

#         # Convert Creation Date and Modified Date to RFC 3339 format
#         creation_date_rfc3339 = meta_data['Creation Date'].astimezone(timezone.utc).isoformat()
#         modified_date_rfc3339 = meta_data['Modified Date'].astimezone(timezone.utc).isoformat()

#         # Define data properties
#         data_props = {
#             "video": b64video, 
#             "filename": video_file.name,
#             "date_created": creation_date_rfc3339,
#             "date_modified": modified_date_rfc3339,
#             "file_size": meta_data['Size (KB)'],
#             "author": '0'  # Set author as placeholder value
#         }

#         # Create data object
#         data_obj = wvc.data.DataObject(properties=data_props, uuid=generate_uuid5(video_file.name))
#         data_objs.append(data_obj)

#     # Insert data objects into Weaviate
#     insert_response = videos_coll.data.insert(data_objs[0])

#     # Print insertion status
#     print(f"{len(insert_response.all_responses)} insertions complete.")
#     print(f"{len(insert_response.errors)} errors within.")
#     if insert_response.has_errors:
#         for e in insert_response.errors:
#             print(e)

#     return insert_response
