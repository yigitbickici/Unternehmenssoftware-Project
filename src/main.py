import sys
sys.path.append('src')

import load_to_chromadb


def main():
    file_path = 'data/databaseCSV.csv'
    data = load_to_chromadb.load_csv(file_path)
    vectors = load_to_chromadb.vectorize_text(data)
    collection = load_to_chromadb.initialize_chromadb()
    load_to_chromadb.load_data_to_chromadb(data, vectors, collection)
    print("Data uploaded successfully.")
    
    results = collection.get(ids=['0', '1', '2'])  
    print("Sorgulanan Veriler:", results)

    total_documents = collection.count()
    print(f"Toplam Yüklenen Veri Sayısı: {total_documents}")


if __name__ == "__main__":
    main()
