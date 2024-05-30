import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from chromadb import Client

def load_csv(file_path):
    """
    CSV dosyasını okur ve gerekli metin kolonunu oluşturur.
    """
    data = pd.read_csv(file_path, delimiter=';')
    data['combined_text'] = data.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    return data

def vectorize_text(data):
    """
    Metin verilerini TF-IDF vektörlerine dönüştürür.
    """
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(data['combined_text'])
    return vectors

def initialize_chromadb():
    """
    ChromaDB istemcisini oluşturur ve koleksiyonu başlatır.
    """
    client = Client()
    collection = client.create_collection(name='my_collection')
    return collection

def load_data_to_chromadb(data, vectors, collection):
    """
    Verileri ChromaDB'ye yükler.
    """
    ids = []
    embeddings = []
    metadatas = []

    for i, row in data.iterrows():
        ids.append(str(i))
        embeddings.append(vectors[i].toarray().tolist()[0])
        metadata = row.to_dict()
        metadatas.append(metadata)

    collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)