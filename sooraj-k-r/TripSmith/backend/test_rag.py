# backend/test_rag.py
from rag_manager import RAGManager

def run_test():
    # Initialize our manager
    rag = RAGManager()
    
    # 1. Process documents (This reads our txt/pdf files and stores them in the DB)
    rag.process_and_store_documents()
    
    # 2. Test a query
    print("\n--- Testing Semantic Search ---")
    query_text = "I want to see tea gardens. Where should I go and how much is the budget?"
    print(f"Query: {query_text}\n")
    
    results = rag.query(query_text)
    
    print("Relevant Information Found:")
    for i, result in enumerate(results, 1):
        print(f"Result {i}: {result}\n")

if __name__ == "__main__":
    run_test()