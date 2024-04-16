import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path
import pandas as pd
import json
from unstructured.partition.pdf import partition_pdf
from AbstractExtractor import AbstractExtractor
from get_metadata import createFileRecords 





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
            ),
            wvc.Property(
                name="pages",
                # data_type=wvc.DataType.OBJECT_ARRAY,
                data_type=wvc.DataType.TEXT_ARRAY,
            ),
            wvc.Property(
                name="num_pages",
                # data_type=wvc.DataType.OBJECT_ARRAY,
                data_type=wvc.DataType.INT,
            ),
            wvc.Property(
                name="date_created",
                # data_type=wvc.DataType.OBJECT_ARRAY,
                data_type=wvc.DataType.DATE,
            ),
            wvc.Property(
                name="date_modified",
                # data_type=wvc.DataType.OBJECT_ARRAY,
                data_type=wvc.DataType.DATE,
            ),
            wvc.Property(
                name="file_size",
                # data_type=wvc.DataType.OBJECT_ARRAY,
                data_type=wvc.DataType.TEXT,
            ),
            wvc.Property(
                name="author",
                # data_type=wvc.DataType.OBJECT_ARRAY,
                data_type=wvc.DataType.TEXT,
            ),


        ],
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            text_fields=[wvc.config.Multi2VecField(name='filename', weight=0.50),
                         wvc.config.Multi2VecField(name='abstract', weight=0.50)],
            vectorize_collection_name=False)
    )

def import_data_pdf(client: WeaviateClient,  collection_name: str = 'pdf') -> BatchObjectReturn:
    

    data_folder = "data/pdf/"

    data_objects = []

    for path in Path(data_folder).iterdir():
        if path.suffix != ".pdf":
            continue
            
        print(f"Processing {path.name}...")

        elements = partition_pdf(filename=path)
        meta_data = createFileRecords(path)

        abstract_extractor = AbstractExtractor()
        abstract_extractor.consume_elements(elements)

        # data_object = {"filename": path.name, "abstract": abstract_extractor.abstract()[:50]}
        data_object = {"filename": path.name, 
                       "abstract": abstract_extractor.abstract()[:50], 
                       "pages":[data.text for data in elements],
                       "num_pages": 0,
                       "date_created":meta_data['Creation Date'].isoformat(),
                       "date_modified":meta_data['Modified Date'].isoformat(),
                       "file_size":meta_data['Size (KB)'],
                       "author": '0'
                       }

        data_objects.append(data_object)



    pdf_collection = client.collections.get('pdf')
    insert_response =pdf_collection.data.insert_many(data_objects)


    print(f"{len(insert_response.all_responses)} insertions complete.")
    print(f"{len(insert_response.errors)} errors within.")
    if insert_response.has_errors:
        for e in insert_response.errors:
            print(e)

    return insert_response


