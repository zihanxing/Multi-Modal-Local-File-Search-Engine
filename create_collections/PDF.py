# Import necessary libraries
import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from scripts.AbstractExtractor import AbstractExtractor
from scripts.get_metadata import createFileRecords 


def define_collection_pdfs(client: WeaviateClient, collection_name: str = 'pdfs') -> bool:
    """
    Define a collection for PDFs in Weaviate.

    Args:
        client (WeaviateClient): The Weaviate client.
        collection_name (str, optional): The name of the collection. Defaults to 'pdfs'.

    Returns:
        bool: True if collection creation is successful, otherwise False.
    """
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
                data_type=wvc.DataType.TEXT_ARRAY,
            ),
            wvc.Property(
                name="num_pages",
                data_type=wvc.DataType.INT,
            ),
            wvc.Property(
                name="date_created",
                data_type=wvc.DataType.DATE,
            ),
            wvc.Property(
                name="date_modified",
                data_type=wvc.DataType.DATE,
            ),
            wvc.Property(
                name="file_size",
                data_type=wvc.DataType.TEXT,
            ),
            wvc.Property(
                name="author",
                data_type=wvc.DataType.TEXT,
            ),
        ],
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            text_fields=[wvc.config.Multi2VecField(name='filename', weight=0.20),
                         wvc.config.Multi2VecField(name='abstract', weight=0.80)],
            vectorize_collection_name=True)
    )
    return True


def import_data_pdf(client: WeaviateClient, collection_name: str = 'pdf') -> BatchObjectReturn:
    """
    Import PDF data into the specified collection in Weaviate.

    Args:
        client (WeaviateClient): The Weaviate client.
        collection_name (str, optional): The name of the collection. Defaults to 'pdf'.

    Returns:
        BatchObjectReturn: The response object containing information about the import process.
    """
    data_folder = "data/pdf/"

    data_objects = []

    for path in Path(data_folder).iterdir():
        if path.suffix != ".pdf":
            continue
            
        print(f"Processing {path.name}...")

        elements = partition_pdf(filename=path)
        meta_data = createFileRecords(path)

        data_object = {"filename": path.name, 
                       "abstract": ' '.join([data.text for data in elements][:20]), 
                       "num_pages": len(elements),
                       "date_created": meta_data['Creation Date'].isoformat(),
                       "date_modified": meta_data['Modified Date'].isoformat(),
                       "file_size": meta_data['Size (KB)'],
                       "author": '0'
                       }

        data_objects.append(data_object)

    pdf_collection = client.collections.get(collection_name)
    insert_response = pdf_collection.data.insert_many(data_objects)

    print(f"{len(insert_response.all_responses)} insertions complete.")
    print(f"{len(insert_response.errors)} errors within.")
    if insert_response.has_errors:
        for e in insert_response.errors:
            print(e)

    return insert_response
