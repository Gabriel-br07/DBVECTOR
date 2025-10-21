"""
Configurações do projeto RAG jurídico.
Carrega variáveis de ambiente com fallbacks sensatos.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se existir
load_dotenv()

# Backend de busca
SEARCH_BACKEND = os.getenv("SEARCH_BACKEND", "faiss")

# Configurações de Embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))
NORMALIZE_EMBEDDINGS = os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true"

# Configurações FAISS
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/indexes/faiss")
FAISS_METADATA_PATH = os.getenv("FAISS_METADATA_PATH", "data/indexes/faiss/metadata.parquet")

# Configurações OpenSearch
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "juridico-docs")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME", "")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "")
OPENSEARCH_USE_SSL = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"

# Query de teste
QUERY = os.getenv("QUERY", "direitos fundamentais")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

def get_opensearch_config() -> dict:
    """Retorna configuração para cliente OpenSearch."""
    config = {
        "hosts": [{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        "use_ssl": OPENSEARCH_USE_SSL,
        "verify_certs": False,
        "ssl_show_warn": False,
    }
    
    if OPENSEARCH_USERNAME and OPENSEARCH_PASSWORD:
        config["http_auth"] = (OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD)
    
    return config