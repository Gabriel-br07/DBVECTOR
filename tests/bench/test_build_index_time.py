"""
Benchmark de tempo de build de índice FAISS.
Valida SLO: MAX_BUILD_TIME_S.
"""
import pytest
import time
import tempfile
import os
from pathlib import Path

from src.schema import get_dummy_docs
from src.storage.faiss_store import FAISSStore
from src import embeddings, config


def test_build_index_dummy_data(benchmark):
    """
    Benchmark de construção de índice FAISS com dados dummy.
    Valida SLO: tempo <= MAX_BUILD_TIME_S.
    """
    # Gera dados dummy expandidos
    base_docs = get_dummy_docs()
    
    # Expande para ~50 docs (replicando com IDs diferentes)
    expanded_docs = []
    for i in range(10):
        for j, doc in enumerate(base_docs):
            new_doc = doc.__class__(
                id=f"{doc.id}_replica_{i}_{j}",
                title=doc.title,
                text=doc.text,
                court=doc.court,
                code=doc.code,
                article=doc.article,
                date=doc.date,
                meta=doc.meta
            )
            expanded_docs.append(new_doc)
    
    def build_index():
        # Cria diretório temporário
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configura paths temporários
            os.environ["FAISS_INDEX_PATH"] = temp_dir
            os.environ["FAISS_METADATA_PATH"] = os.path.join(temp_dir, "metadata.parquet")
            
            # Cria store e indexa
            store = FAISSStore()
            store.index(expanded_docs)
            
            # Limpa environment
            os.environ.pop("FAISS_INDEX_PATH", None)
            os.environ.pop("FAISS_METADATA_PATH", None)
            
            return store
    
    # Executa benchmark
    result = benchmark(build_index)
    
    # Obtém estatísticas
    stats = result.stats
    mean_time = stats.mean
    
    print(f"\n📊 Build Index Performance:")
    print(f"   Documentos: {len(expanded_docs)}")
    print(f"   Tempo médio: {mean_time:.2f}s")
    print(f"   SLO: {config.MAX_BUILD_TIME_S}s")
    
    # Valida SLO
    assert mean_time <= config.MAX_BUILD_TIME_S, \
        f"Build time exceeded: {mean_time:.2f}s > {config.MAX_BUILD_TIME_S}s"


def test_build_index_incremental(benchmark):
    """
    Benchmark de build incremental (adicionar documentos a índice existente).
    """
    base_docs = get_dummy_docs()
    
    def build_incremental():
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["FAISS_INDEX_PATH"] = temp_dir
            os.environ["FAISS_METADATA_PATH"] = os.path.join(temp_dir, "metadata.parquet")
            
            # Build inicial
            store = FAISSStore()
            store.index(base_docs[:3])
            
            # Adiciona mais documentos
            store.index(base_docs[3:])
            
            os.environ.pop("FAISS_INDEX_PATH", None)
            os.environ.pop("FAISS_METADATA_PATH", None)
            
            return store
    
    result = benchmark(build_incremental)
    mean_time = result.stats.mean
    
    print(f"\n📊 Incremental Build:")
    print(f"   Tempo médio: {mean_time:.2f}s")
    
    # Build incremental deve ser rápido (< MAX_BUILD_TIME_S / 2)
    max_incremental = config.MAX_BUILD_TIME_S / 2
    
    assert mean_time <= max_incremental, \
        f"Incremental build too slow: {mean_time:.2f}s > {max_incremental:.2f}s"


def test_embedding_generation_time(benchmark):
    """
    Benchmark isolado de geração de embeddings.
    Útil para identificar bottleneck.
    """
    texts = [doc.text for doc in get_dummy_docs()] * 10  # 50 textos
    
    def generate_embeddings():
        return embeddings.encode_texts(texts)
    
    result = benchmark(generate_embeddings)
    mean_time = result.stats.mean
    
    print(f"\n📊 Embedding Generation:")
    print(f"   Textos: {len(texts)}")
    print(f"   Tempo médio: {mean_time:.2f}s")
    print(f"   Tempo/doc: {(mean_time / len(texts)) * 1000:.2f}ms")
    
    # Embedding deve ser razoavelmente rápido
    # ~20ms por documento em média
    max_per_doc_ms = 50
    actual_per_doc_ms = (mean_time / len(texts)) * 1000
    
    assert actual_per_doc_ms <= max_per_doc_ms, \
        f"Embedding too slow: {actual_per_doc_ms:.2f}ms/doc > {max_per_doc_ms}ms/doc"


def test_faiss_index_construction_only(benchmark):
    """
    Benchmark apenas da construção do índice FAISS (sem embeddings).
    """
    # Pre-gera embeddings
    docs = get_dummy_docs() * 10
    texts = [doc.text for doc in docs]
    vectors = embeddings.encode_texts(texts)
    
    def construct_faiss_index():
        import faiss
        import numpy as np
        
        dim = vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        
        # Normaliza se necessário
        if config.NORMALIZE_EMBEDDINGS:
            faiss.normalize_L2(vectors)
        
        index.add(vectors)
        return index
    
    result = benchmark(construct_faiss_index)
    mean_time = result.stats.mean
    
    print(f"\n📊 FAISS Index Construction:")
    print(f"   Vetores: {len(vectors)}")
    print(f"   Dimensão: {vectors.shape[1]}")
    print(f"   Tempo: {mean_time * 1000:.2f}ms")
    
    # Construção do índice FAISS deve ser muito rápida (< 1s para 50 docs)
    assert mean_time < 1.0, \
        f"FAISS construction too slow: {mean_time:.2f}s"


def test_metadata_save_time(benchmark):
    """
    Benchmark de salvamento de metadados (Parquet).
    """
    docs = get_dummy_docs() * 10
    
    def save_metadata():
        import pandas as pd
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = Path(temp_dir) / "metadata.parquet"
            
            # Converte docs para DataFrame
            data = [doc.to_dict() for doc in docs]
            df = pd.DataFrame(data)
            
            # Salva
            df.to_parquet(metadata_path, index=False)
            
            return metadata_path
    
    result = benchmark(save_metadata)
    mean_time = result.stats.mean
    
    print(f"\n📊 Metadata Save:")
    print(f"   Documentos: {len(docs)}")
    print(f"   Tempo: {mean_time * 1000:.2f}ms")
    
    # Salvamento deve ser rápido (< 500ms para 50 docs)
    assert mean_time < 0.5, \
        f"Metadata save too slow: {mean_time:.2f}s"


def test_full_pipeline_benchmark():
    """
    Teste end-to-end do pipeline completo de build.
    Não usa pytest-benchmark, mas mede tempo total.
    """
    docs = get_dummy_docs() * 10
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["FAISS_INDEX_PATH"] = temp_dir
        os.environ["FAISS_METADATA_PATH"] = os.path.join(temp_dir, "metadata.parquet")
        
        start = time.time()
        
        # Pipeline completo
        store = FAISSStore()
        store.index(docs)
        
        # Testa busca
        query_vec = embeddings.encode_single_text("teste")
        results = store.search(query_vec, k=5)
        
        elapsed = time.time() - start
        
        os.environ.pop("FAISS_INDEX_PATH", None)
        os.environ.pop("FAISS_METADATA_PATH", None)
    
    print(f"\n📊 Full Pipeline:")
    print(f"   Documentos: {len(docs)}")
    print(f"   Tempo total: {elapsed:.2f}s")
    print(f"   Busca funcionou: {len(results) > 0}")
    
    # Pipeline completo deve respeitar SLO
    assert elapsed <= config.MAX_BUILD_TIME_S, \
        f"Full pipeline too slow: {elapsed:.2f}s > {config.MAX_BUILD_TIME_S}s"
