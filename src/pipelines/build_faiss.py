"""
Pipeline para indexar documentos dummy no FAISS.
"""
import sys
from pathlib import Path

# Adiciona src ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.storage.factory import get_faiss_store
from src.schema import get_dummy_docs


def main():
    """Indexa documentos dummy no FAISS."""
    print("🚀 Iniciando pipeline de build FAISS...")
    
    # Carrega documentos dummy
    docs = get_dummy_docs()
    print(f"📄 Carregados {len(docs)} documentos dummy")
    
    # Cria store FAISS
    store = get_faiss_store()
    
    # Indexa documentos  
    store.index(docs)
    
    print(f"✅ Pipeline concluído! {store.get_doc_count()} documentos indexados")
    
    # Mostra resumo dos documentos
    print("\n📋 Documentos indexados:")
    for doc in docs:
        print(f"  • {doc.id}: {doc.title}")


if __name__ == "__main__":
    main()