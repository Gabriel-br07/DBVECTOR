"""
Configuração de fixtures para testes.
"""
import os
import tempfile
import pytest
from typing import List
import numpy as np

from src.schema import Doc, get_dummy_docs
from src import embeddings


@pytest.fixture
def dummy_docs() -> List[Doc]:
    """Fixture com documentos dummy para testes."""
    return get_dummy_docs()


@pytest.fixture
def sample_doc() -> Doc:
    """Fixture com um documento simples para testes."""
    return Doc(
        id="test_doc_1",
        title="Documento de Teste",
        text="Este é um documento de teste para verificar funcionalidades do sistema RAG jurídico.",
        court="Teste",
        code="TEST",
        article="1",
        date="2024-01-01"
    )


@pytest.fixture
def dummy_vectors(dummy_docs) -> np.ndarray:
    """Fixture com embeddings dos documentos dummy."""
    texts = [doc.text for doc in dummy_docs]
    return embeddings.encode_texts(texts)


@pytest.fixture
def temp_faiss_path():
    """Fixture com diretório temporário para índices FAISS."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Configura paths temporários via environment
        os.environ["FAISS_INDEX_PATH"] = temp_dir
        os.environ["FAISS_METADATA_PATH"] = os.path.join(temp_dir, "metadata.parquet")
        yield temp_dir
        # Limpa environment após teste
        os.environ.pop("FAISS_INDEX_PATH", None)
        os.environ.pop("FAISS_METADATA_PATH", None)


@pytest.fixture
def opensearch_test_index():
    """Fixture que retorna nome de índice de teste para OpenSearch."""
    return "test-juridico-docs"


@pytest.fixture
def query_vector() -> np.ndarray:
    """Fixture com vetor de query para testes."""
    return embeddings.encode_single_text("direitos fundamentais constitucionais")