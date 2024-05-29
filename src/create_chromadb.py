import chromadb
from chromadb.config import Settings

def create_chromadb_collection(name="my_collection"):
    
    client = chromadb.Client(Settings())
    collection = client.create_collection(name=name)
    return collection

def add_data_to_collection(collection, df):
   
    for index, row in df.iterrows():
        vector = row.tolist()
        metadata = row.fillna('').to_dict()  # NaN değerlerini boş bir dizeyle doldur
        document = {
            "id": str(index),
            "vector": vector,
            "metadata": metadata
        }
        collection.add([document])  # Koleksiyona belge eklemek için uygun metodu kullanın
