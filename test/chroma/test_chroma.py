# test_chroma.py
from chroma import get_or_create_collection

def test_chroma():
    collection = get_or_create_collection("test_docs")
    collection.add(
        ids=["1"],
        documents=["Привет, это тестовый документ для ChromaDB"]
    )
    results = collection.get(ids=["1"])
    print("✅ Результат:", results)

if __name__ == "__main__":
    test_chroma()
