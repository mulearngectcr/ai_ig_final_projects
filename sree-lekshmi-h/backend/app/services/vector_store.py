import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB
client = chromadb.PersistentClient(
    path="./recipe_db"
)

# Create collection
collection = client.get_or_create_collection(
    name="recipe_knowledge"
)

# Load embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def split_text(text, chunk_size=500, overlap=50):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def store_recipe_text(filename, text):

    chunks = split_text(text)

    embeddings = embedding_model.encode(chunks).tolist()

    ids = [
        f"{filename}_{i}"
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {"filename": filename}
            for _ in chunks
        ]
    )

    return len(chunks)

def search_recipe_text(question, n_results=3):

    # Convert question into an embedding
    question_embedding = embedding_model.encode(
        [question]
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=n_results
    )

    return results["documents"][0]

def get_uploaded_pdfs():
    results = collection.get(include=["metadatas"])

    filenames = set()

    for metadata in results["metadatas"]:
        filenames.add(metadata["filename"])

    return sorted(filenames)


def delete_recipe_pdf(filename):
    collection.delete(
        where={"filename": filename}
    )
    return True