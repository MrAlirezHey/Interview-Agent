import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import logging
embeding_model=SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
client=chromadb.PersistentClient(path='./chromadb')
profile_collection=client.get_or_create_collection(name='profiles')
def index_profile(profile_id:int , txt_content:str):
    if not txt_content:
        return
    embedding=embeding_model.encode(txt_content).tolist()
    profile_collection.upsert(
        ids=str(profile_id),
        embeddings=[embedding],
        documents=[txt_content],
        metadatas=[{'profile_id':profile_id}]
    )
    logging.info(f"Indexing profile with ID {profile_id} into ChromaDB.")
def search_similar_profiles(query:str,top_n: int=3):
    logging.info(f"Performing semantic search in ChromaDB for query: '{query}'")
    query_embedding=embeding_model.encode(query).tolist()
    results=profile_collection.query(query_embeddings=query_embedding,
                                     n_results=top_n)
    if results and results['metadatas'][0]:
        return [meta['profile_id'] for meta in results['metadatas'][0]] 
    return []
