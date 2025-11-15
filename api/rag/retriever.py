import logging
import os
from pathlib import Path
from typing import List, Dict

import chromadb
from chromadb.config import Settings

os.environ.setdefault("CHROMADB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

logging.getLogger("chromadb.telemetry").setLevel(logging.CRITICAL)
logging.getLogger("chromadb.telemetry.telemetry").setLevel(logging.CRITICAL)
logging.getLogger("chromadb.telemetry.product").setLevel(logging.CRITICAL)


def retrieve(query: str, k: int = 4) -> List[Dict[str, str]]:
    """
    Retrieve relevant chunks from the vector database
    
    Args:
        query: Search query
        k: Number of results to return
        
    Returns:
        List of dictionaries with 'chunk' and 'id' keys
    """
    try:
        # Get the correct path
        script_dir = Path(__file__).parent
        chroma_path = script_dir / "chroma_db"
        
        # Initialize Chroma client
        chroma_client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )
        
        # Try to get collection - handle corruption gracefully
        try:
            collection = chroma_client.get_collection("medical_knowledge")
        except Exception as collection_error:
            # If collection is corrupted or doesn't exist, return empty results
            error_msg = str(collection_error)
            if "object of type 'int' has no len()" in error_msg or "TypeError" in str(type(collection_error).__name__):
                print(f"ChromaDB collection appears corrupted. Returning empty results. Error: {error_msg}")
            else:
                print(f"Failed to get ChromaDB collection: {error_msg}")
            return []
        
        # Query the collection - handle internal ChromaDB errors
        try:
            results = collection.query(
                query_texts=[query],
                n_results=k
            )
        except TypeError as te:
            # Handle ChromaDB internal corruption errors
            if "object of type 'int' has no len()" in str(te):
                print(f"ChromaDB database corruption detected during query. Returning empty results.")
                print(f"Error details: {te}")
                return []
            raise
        
        # Format results
        retrieved = []
        # Safely check if documents exist and is a list
        documents_raw = results.get("documents")
        if documents_raw and isinstance(documents_raw, list) and len(documents_raw) > 0:
            # Safely extract documents
            documents = documents_raw[0] if isinstance(documents_raw[0], list) else []
            
            # Safely extract ids - ensure it's a list
            ids_raw = results.get("ids", [])
            if isinstance(ids_raw, list) and len(ids_raw) > 0:
                ids = ids_raw[0] if isinstance(ids_raw[0], list) else []
            else:
                ids = []
            
            # Safely extract metadatas - ensure it's a list
            metadatas_raw = results.get("metadatas", [])
            if isinstance(metadatas_raw, list) and len(metadatas_raw) > 0:
                metadatas = metadatas_raw[0] if isinstance(metadatas_raw[0], list) else []
            else:
                metadatas = []
            
            # Ensure all are lists before calculating min_length
            if not isinstance(documents, list):
                documents = []
            if not isinstance(ids, list):
                ids = []
            if not isinstance(metadatas, list):
                metadatas = []
            
            # Ensure all lists have the same length
            lengths = [len(documents), len(ids), len(metadatas)]
            min_length = min(lengths) if lengths else 0
            
            for i in range(min_length):
                chunk = documents[i] if i < len(documents) else ""
                chunk_id = ids[i] if i < len(ids) else f"unknown_{i}"
                metadata = metadatas[i] if i < len(metadatas) and isinstance(metadatas[i], dict) else {}
                
                retrieved.append({
                    "chunk": chunk,
                    "id": chunk_id,
                    "source": metadata.get("source", metadata.get("source_file", "unknown")),
                    "source_file": metadata.get("source_file", "unknown"),
                    "category": metadata.get("category", "general"),
                    "title": metadata.get("title", metadata.get("topic", "unknown")),
                    "topic": metadata.get("topic", metadata.get("title", "unknown")),
                })
        
        return retrieved
    
    except TypeError as te:
        # Handle ChromaDB internal corruption errors (object of type 'int' has no len())
        if "object of type 'int' has no len()" in str(te) or "has no len()" in str(te):
            print(f"ChromaDB database corruption detected. Returning empty results.")
            print(f"Error: {te}")
            print("Note: The ChromaDB database may need to be rebuilt. Run 'python api/rag/build_index.py' to rebuild.")
            return []
        # Re-raise if it's a different TypeError
        raise
    except Exception as e:
        import traceback
        error_str = str(e)
        # Check if it's the ChromaDB corruption error
        if "object of type 'int' has no len()" in error_str or "has no len()" in error_str:
            print(f"ChromaDB database corruption detected. Returning empty results.")
            print(f"Error: {e}")
            print("Note: The ChromaDB database may need to be rebuilt. Run 'python api/rag/build_index.py' to rebuild.")
            return []
        
        print(f"Retrieval error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        # Log the results structure for debugging
        try:
            if 'results' in locals():
                print(f"Results type: {type(results)}")
                print(f"Results keys: {results.keys() if isinstance(results, dict) else 'Not a dict'}")
                if isinstance(results, dict):
                    for key, value in results.items():
                        if isinstance(value, (list, dict)):
                            item_count = len(value) if hasattr(value, "__len__") else "no len"
                            value_str = f"{type(value).__name__} with {item_count} items"
                        else:
                            value_str = str(value)[:100]
                        print(f"  {key}: type={type(value).__name__}, value={value_str}")
        except:
            pass
        return []


def test_retrieval():
    """Test the retrieval function"""
    test_queries = [
        "I have fever and body ache",
        "What should I do for sore throat?",
        "Chest pain and shortness of breath"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = retrieve(query, k=2)
        for r in results:
            print(f"  📄 {r['source']}: {r['chunk'][:100]}...")


if __name__ == "__main__":
    test_retrieval()