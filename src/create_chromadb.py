import chromadb
from chromadb.config import Settings

def create_chromadb_collection(name="my_collection"):
    client = chromadb.Client(Settings())
    collection = client.create_collection(name=name)
    return collection

def add_data_to_collection(collection, df):
    counter = 0
    for _, row in df.iterrows():
        vector = row.tolist()
        metadata = {}  # Boş bir metadata sözlüğü oluştur
        # Her bir sütunun adı ve değeri için metadata sözlüğüne ekleyin
        for column_name, value in row.items():
            metadata[column_name] = value
        document = {
            "id": str(counter),
            "vector": vector,
            "metadata": metadata
        }
        collection.add([document])
        counter += 1
