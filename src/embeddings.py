"""
Geração de embeddings usando sentence-transformers.
"""
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from src import config

# Singleton para o modelo
_model: Optional[SentenceTransformer] = None


def load_model() -> SentenceTransformer:
    """Carrega o modelo de embedding (singleton)."""
    global _model
    if _model is None:
        print(f"🔄 Carregando modelo: {config.EMBEDDING_MODEL}")
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
        print(f"✅ Modelo carregado! Dimensão: {_model.get_sentence_embedding_dimension()}")
    return _model


def encode_texts(texts: List[str]) -> np.ndarray:
    """
    Gera embeddings para lista de textos.
    
    Args:
        texts: Lista de textos para embeddings
        
    Returns:
        Array numpy de embeddings com shape (len(texts), embedding_dim)
        Tipo: np.float32
        Normalizado se config.NORMALIZE_EMBEDDINGS=True
    """
    model = load_model()
    
    # Gera embeddings
    embeddings = model.encode(
        texts,
        normalize_embeddings=config.NORMALIZE_EMBEDDINGS,
        show_progress_bar=len(texts) > 10,
        convert_to_numpy=True
    )
    
    # Garante tipo float32 para compatibilidade FAISS
    return embeddings.astype(np.float32)


def encode_single_text(text: str) -> np.ndarray:
    """
    Gera embedding para um único texto.
    
    Args:
        text: Texto para embedding
        
    Returns:
        Array numpy com shape (embedding_dim,)
    """
    embeddings = encode_texts([text])
    return embeddings[0]


def get_embedding_dimension() -> int:
    """Retorna a dimensão dos embeddings do modelo atual."""
    model = load_model()
    return model.get_sentence_embedding_dimension()