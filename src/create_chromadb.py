import chromadb
from chromadb.config import Settings
import pandas as pd

def create_chromadb_collection(name="my_collection"):
    client = chromadb.Client(Settings())
    collection = client.create_collection(name=name)
    return collection

def add_data_to_collection(collection, df):
    counter = 0
    documents = []
    for _, row in df.iterrows():
        vector = [str(value) for value in row.tolist()]
        metadata = {column_name: str(value) for column_name, value in row.items()}
        document = {
            "id": str(counter),
            "vector": vector,
            "metadata": metadata
        }
        documents.append(document)
        counter+=1
    collection.add(documents)
