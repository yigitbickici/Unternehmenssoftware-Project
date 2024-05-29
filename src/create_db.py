import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings())

collection = client.create_collection(name="my_collection")

for index, row in df.iterrows():
    vector = row.tolist()
    collection.add_document(document_id=str(index), vector=vector, metadata=row.to_dict())

print("csv uploaded successfully")
