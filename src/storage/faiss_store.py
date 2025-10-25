"""
Store FAISS para busca vetorial local.
"""
import os
import faiss
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path

from src.storage.base import VectorStore
from src.schema import Doc, SearchResult
from src import embeddings, config


class FAISSStore(VectorStore):
    """Store FAISS com persistência local."""
    
    def __init__(self, index_path: str = None, metadata_path: str = None):
        # Permite sobrescrever via variáveis de ambiente em tempo de execução
        self.index_path = index_path or os.getenv("FAISS_INDEX_PATH", config.FAISS_INDEX_PATH)
        self.metadata_path = metadata_path or os.getenv("FAISS_METADATA_PATH", config.FAISS_METADATA_PATH)
        self._index = None
        self.metadata = {}
        
        # Cria diretórios se necessário
        Path(self.index_path).mkdir(parents=True, exist_ok=True)
        
        # Carrega index existente se houver
        self._load_index()
    
    def _get_index_file(self) -> str:
        """Retorna caminho do arquivo de índice FAISS."""
        return os.path.join(self.index_path, "index.faiss")
    
    def _load_index(self) -> None:
        """Carrega índice FAISS e metadados se existirem."""
        index_file = self._get_index_file()
        
        if os.path.exists(index_file):
            print(f"📁 Carregando índice FAISS: {index_file}")
            self._index = faiss.read_index(index_file)

            # Carrega metadados
            if os.path.exists(self.metadata_path):
                df = pd.read_parquet(self.metadata_path)
                self.metadata = df.set_index('internal_id').to_dict('index')
                print(f"✅ Índice carregado! {len(self.metadata)} documentos")
            else:
                print("⚠️ Arquivo de metadados não encontrado")
        else:
            print("📝 Nenhum índice FAISS encontrado - será criado novo")
    
    def _save_index(self) -> None:
        """Salva índice FAISS e metadados no disco."""
        if self._index is None:
            return
            
        index_file = self._get_index_file()
        print(f"💾 Salvando índice FAISS: {index_file}")
        faiss.write_index(self._index, index_file)

        # Salva metadados
        if self.metadata:
            df = pd.DataFrame.from_dict(self.metadata, orient='index')
            df.index.name = 'internal_id'
            df.reset_index(inplace=True)
            df.to_parquet(self.metadata_path, index=False)
            print(f"💾 Metadados salvos: {self.metadata_path}")
    
    def _doc_to_internal_id(self, doc_id: str) -> int:
        """Converte ID do documento para ID interno FAISS (simples hash)."""
        return hash(doc_id) % (2**31 - 1)  # Positivo int32
    
    def index(self, docs: List[Doc]) -> None:
        """Indexa documentos no FAISS."""
        if not docs:
            return
            
        print(f"🔄 Indexando {len(docs)} documentos no FAISS...")
        
        # Gera embeddings
        texts = [doc.text for doc in docs]
        vectors = embeddings.encode_texts(texts)
        
        # Cria índice se não existir
        if self._index is None:
            dimension = vectors.shape[1]
            print(f"📊 Criando índice FAISS com dimensão {dimension}")
            
            # Usa IndexFlatIP para busca por produto interno (cosseno se normalizado)
            base_index = faiss.IndexFlatIP(dimension)
            # Usa IndexIDMap2 para manter mapeamento de IDs
            self._index = faiss.IndexIDMap2(base_index)

        # Prepara IDs internos e metadados
        internal_ids = []
        for doc in docs:
            internal_id = self._doc_to_internal_id(doc.id)
            internal_ids.append(internal_id)
            
            # Armazena metadados
            self.metadata[internal_id] = {
                'id': doc.id,
                'title': doc.title,
                'text': doc.text,
                'court': doc.court,
                'code': doc.code,
                'article': doc.article,
                'date': doc.date,
                'meta': doc.meta
            }
        
        # Adiciona ao índice
        self._index.add_with_ids(vectors, np.array(internal_ids, dtype=np.int64))

        # Salva no disco
        self._save_index()
        print(f"✅ {len(docs)} documentos indexados com sucesso!")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[SearchResult]:
        """Busca documentos similares."""
        if self._index is None or self._index.ntotal == 0:
            print("⚠️ Índice vazio ou não inicializado")
            return []
        
        # Garante que query_vector é 2D
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Busca no FAISS
        scores, internal_ids = self._index.search(query_vector, k)

        results = []
        for score, internal_id in zip(scores[0], internal_ids[0]):
            if internal_id == -1:  # ID inválido
                continue
                
            if internal_id in self.metadata:
                doc_data = self.metadata[internal_id]
                doc = Doc(
                    id=doc_data['id'],
                    text=doc_data['text'],
                    title=doc_data['title'],
                    court=doc_data['court'],
                    code=doc_data['code'],
                    article=doc_data['article'],
                    date=doc_data['date'],
                    meta=doc_data['meta']
                )
                results.append(SearchResult(doc=doc, score=float(score)))
        
        return results
    
    def get_doc_count(self) -> int:
        """Retorna número de documentos indexados."""
        if self._index is None:
            return 0
        return self._index.ntotal
