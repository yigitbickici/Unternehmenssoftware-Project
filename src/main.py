import sys
sys.path.append('src')

from load_data import load_csv
from create_chromadb import create_chromadb_collection, add_data_to_collection

def main():
    csv_file_path = 'data/databaseCSV - Sayfa1.csv'
    
    df = load_csv(csv_file_path)
    
    collection = create_chromadb_collection(name="my_collection")
    
    add_data_to_collection(collection, df)
    
    print("CSV file uploaded.")

if __name__ == "__main__":
    main()
