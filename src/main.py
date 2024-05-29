import sys
sys.path.append('src')

from load_data import load_csv
from create_chromadb import create_chromadb_collection, add_data_to_collection

def main():
    # CSV dosyasının yolu
    csv_file_path = 'data/databaseCSV - Sayfa1.csv'
    
    # CSV dosyasını yükle
    df = load_csv(csv_file_path)
    
    # ChromaDB koleksiyonunu oluştur
    collection = create_chromadb_collection(name="my_collection")
    
    # Verileri ChromaDB koleksiyonuna ekle
    add_data_to_collection(collection, df)
    
    print("CSV dosyası başarıyla ChromaDB'ye yüklendi.")

if __name__ == "__main__":
    main()
