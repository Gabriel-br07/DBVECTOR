# 🏛️ RAG Jurídico

Sistema de **Retrieval-Augmented Generation (RAG)** para documentos jurídicos com busca vetorial, desenvolvido para começar com **FAISS** local e migrar facilmente para **OpenSearch** distribuído.

## 🎯 Visão Geral

Este projeto oferece uma infraestrutura completa de RAG jurídico com:

- **Busca vetorial** com embeddings semânticos (sentence-transformers)
- **Dois backends intercambiáveis**: FAISS (local) e OpenSearch (distribuído)
- **API REST** com FastAPI para integração
- **Testes abrangentes** com pytest (unitários e integração)
- **Dados dummy** para validação imediata
- **Pipeline pronto** para plugar JSONs reais

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API FastAPI   │    │   Embeddings     │    │  Vector Store   │
│  /search        │◄──►│ sentence-transf. │◄──►│ FAISS/OpenSrch │
│  /health        │    │ all-MiniLM-L6-v2 │    │ cosine similarity│
│  /docs          │    │ dim=384          │    │ k-NN search     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Pré-requisitos

- **Python 3.10+**
- **Poetry** (gerenciador de dependências Python)
- **Docker** (opcional, para OpenSearch)
- **Git**

### Instalação do Poetry

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Linux/Mac
curl -sSL https://install.python-poetry.org | python3 -

# Ou via pip (alternativa)
pip install poetry
```

## 🚀 Instalação Rápida

### 1. Clone e Configure

```bash
git clone <repo-url>
cd rag-juridico

# Opção 1: Poetry (recomendado)
poetry install

# Ativa ambiente virtual
poetry shell

# Opção 2: Fallback pip (se Poetry falhar no Windows)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

> **📝 Nota Windows**: Se Poetry falhar por falta de compiladores (Visual Studio Build Tools), use o fallback pip. Veja [INSTALL.md](INSTALL.md) para detalhes.

### 2. Configuração

```bash
# Cria arquivo de configuração
cp .env.example .env

# Edite .env se necessário (valores padrão funcionam para desenvolvimento)
```

### 3. Setup FAISS (Recomendado para início)

```bash
# Indexa documentos dummy
make faiss-build
# ou: poetry run python -m src.pipelines.build_faiss

# Testa busca via pipeline
make faiss-query
# ou: poetry run python -m src.pipelines.query_faiss

# Inicia API
make api
# ou: poetry run uvicorn src.api.main:app --reload --port 8000
```

Pronto! Acesse http://localhost:8000/docs para documentação interativa.

## ⚙️ Configuração (.env)

```bash
# Backend de busca (faiss|opensearch)
SEARCH_BACKEND=faiss

# Configurações de Embedding
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIM=384
NORMALIZE_EMBEDDINGS=true

# FAISS (backend local)
FAISS_INDEX_PATH=data/indexes/faiss
FAISS_METADATA_PATH=data/indexes/faiss/metadata.parquet

# OpenSearch (backend distribuído) 
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_INDEX=juridico-docs
OPENSEARCH_USE_SSL=false

# Query de teste para pipelines
QUERY=direitos fundamentais

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 🔄 Workflows

### Backend FAISS (Desenvolvimento Local)

```bash
# 1. Instala dependências
make install
# ou: poetry install

# 2. Indexa documentos dummy
make faiss-build

# 3. Testa busca via pipeline
make faiss-query

# 4. Inicia API
make api

# 5. Testa API
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"q": "direitos fundamentais", "k": 3}'
```

### Migração para OpenSearch

```bash
# 1. Inicia OpenSearch via Docker
make os-up

# 2. Aguarda inicialização (aguarde ~30s)
make os-build

# 3. Altera backend no .env
SEARCH_BACKEND=opensearch

# 4. Testa busca
make os-query

# 5. Reinicia API (automaticamente usa OpenSearch)
make api
```

### Comandos Makefile

| Comando | Descrição |
|---------|-----------|
| `make install` | Instala dependências com Poetry |
| `make shell` | Ativa ambiente virtual Poetry |
| `make format` | Formata código (black + isort) |
| `make lint` | Verifica formatação e estilo |
| `make faiss-build` | Indexa docs no FAISS |
| `make faiss-query` | Busca no FAISS |
| `make os-up` | Inicia OpenSearch (Docker) |
| `make os-down` | Para OpenSearch |
| `make os-build` | Indexa docs no OpenSearch |
| `make os-query` | Busca no OpenSearch |
| `make api` | Inicia API FastAPI |
| `make test` | Executa todos os testes |
| `make test-cov` | Testes com cobertura |
| `make demo` | Script de demonstração |

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
make test
# ou: poetry run pytest tests/ -v

# Com cobertura
make test-cov
# ou: poetry run pytest tests/ --cov=src --cov-report=html

# Apenas FAISS
poetry run pytest tests/test_faiss_store.py -v

# Apenas API
poetry run pytest tests/test_api_faiss.py -v

# OpenSearch (requer serviço rodando)
make os-up
poetry run pytest tests/test_opensearch_store.py -v
```

### Estrutura de Testes

- **test_embeddings.py**: Testa geração de embeddings
- **test_faiss_store.py**: Testa store FAISS
- **test_opensearch_store.py**: Testa store OpenSearch (condicional)
- **test_api_faiss.py**: Testa API de ponta a ponta

Testes de OpenSearch são **automaticamente ignorados** se o serviço não estiver disponível.

## 📊 Dados Dummy

O projeto inclui 5 documentos jurídicos dummy para validação:

1. **Constituição Federal Art. 5º** - Direitos fundamentais
2. **STF HC 123.456** - Habeas corpus e liberdade
3. **Código Civil Art. 197** - Prescrição entre cônjuges  
4. **Código Civil Art. 178** - Decadência de negócios jurídicos
5. **STJ REsp 987.654** - Responsabilidade do consumidor

## 🔧 Como Plugar JSONs Reais

### 1. Criar Normalizador

```python
# src/data_loader.py
from src.schema import Doc
import json

def load_from_json(json_path: str) -> List[Doc]:
    """Carrega documentos de arquivo JSON real."""
    with open(json_path) as f:
        data = json.load(f)
    
    docs = []
    for item in data:
        # Adapte campos conforme seu JSON
        doc = Doc(
            id=item["id"],
            text=item["texto_completo"],  # Campo principal para busca
            title=item.get("titulo"),
            court=item.get("tribunal"),
            code=item.get("codigo"),
            article=item.get("artigo"), 
            date=item.get("data"),
            meta=item.get("metadados", {})
        )
        docs.append(doc)
    
    return docs
```

### 2. Atualizar Pipeline

```python
# src/pipelines/build_real_data.py
from src.data_loader import load_from_json
from src.storage.factory import get_store

def main():
    # Carrega dados reais
    docs = load_from_json("data/documentos_juridicos.json")
    
    # Indexa no backend configurado
    store = get_store()
    store.index(docs)
```

### 3. Campo Text Canônico

Para documentos complexos, concatene campos relevantes:

```python
def create_canonical_text(item: dict) -> str:
    """Cria texto canônico para busca."""
    parts = []
    
    if item.get("titulo"):
        parts.append(item["titulo"])
    
    if item.get("ementa"):
        parts.append(item["ementa"])
        
    if item.get("texto_completo"):
        parts.append(item["texto_completo"])
    
    return " ".join(parts)
```

## 🚀 Próximos Passos

### Funcionalidades Avançadas

1. **Busca Híbrida** (BM25 + kNN)
   - Implementar no OpenSearch
   - Combinar busca lexical e semântica

2. **Filtros Estruturados**
   - Por tribunal, data, tipo de documento
   - Filtros combinados com busca vetorial

3. **Avaliação de Qualidade**
   - Métricas nDCG@k, MRR
   - Dataset de relevância manual

4. **Otimizações**
   - Cache de embeddings
   - Quantização de vetores
   - Sharding para grandes volumes

### Ambiente de Produção

1. **Segurança OpenSearch**
   ```yaml
   # docker-compose.prod.yml
   services:
     opensearch:
       environment:
         - plugins.security.disabled=false
         - OPENSEARCH_INITIAL_ADMIN_PASSWORD=<senha-forte>
   ```

2. **Monitoramento**
   - Logs estruturados
   - Métricas de latência
   - Health checks

3. **Escalabilidade**
   - Load balancer para API
   - Cluster OpenSearch multi-nó
   - Cache Redis para queries frequentes

## 📚 API Reference

### POST /search

Busca documentos por similaridade semântica.

**Request:**
```json
{
  "q": "direitos fundamentais constitucionais",
  "k": 5
}
```

**Response:**
```json
{
  "query": "direitos fundamentais constitucionais",
  "total": 3,
  "backend": "faiss",
  "results": [
    {
      "id": "cf88_art5",
      "title": "Constituição Federal - Art. 5º",
      "text": "Todos são iguais perante a lei...",
      "court": "Constituição Federal",
      "code": "CF/88",
      "article": "5º",
      "date": "1988-10-05",
      "score": 0.8956
    }
  ]
}
```

### Endpoints Auxiliares

- `GET /` - Informações da API
- `GET /health` - Health check
- `GET /docs` - Documentação Swagger
- `GET /redoc` - Documentação ReDoc

## � Gerenciamento de Dependências com Poetry

Este projeto usa **Poetry** para gerenciamento moderno de dependências e ambientes virtuais.

### Comandos Poetry Úteis

```bash
# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell

# Executar comandos no ambiente virtual
poetry run python script.py
poetry run pytest
poetry run uvicorn src.api.main:app

# Adicionar nova dependência
poetry add requests
poetry add --group dev black  # dependência de desenvolvimento

# Atualizar dependências
poetry update

# Mostrar dependências
poetry show
poetry show --tree

# Informações do ambiente
poetry env info
poetry env list

# Exportar requirements.txt (se necessário)
poetry export -f requirements.txt --output requirements.txt
poetry export --with dev -f requirements.txt --output requirements-dev.txt
```

### Vantagens do Poetry

- **Resolução automática** de conflitos de dependências
- **Lock file** (`poetry.lock`) para builds reproduzíveis  
- **Ambiente virtual** gerenciado automaticamente
- **Build e publicação** de pacotes Python
- **Configuração unificada** em `pyproject.toml`

## �🐛 Troubleshooting

### FAISS

**Erro: "No module named 'faiss'"**
```bash
poetry add faiss-cpu
```

**Erro: "Poetry not found"**
```bash
# Instale Poetry primeiro
curl -sSL https://install.python-poetry.org | python3 -
# ou: pip install poetry
```

**Erro: "Index file not found"**
```bash
make faiss-build  # Reconstrói índice
```

### OpenSearch

**Erro: "Connection refused"**
```bash
make os-up  # Inicia container
docker logs opensearch-rag  # Verifica logs
```

**Erro: "Index not found"**
```bash
make os-build  # Cria índice e indexa docs
```

### API

**Erro 503: "Store não inicializado"**
- Verifique se backend está configurado
- Execute pipeline de build antes da API

**Erro 404: "Nenhum documento indexado"**
```bash
# Para FAISS
make faiss-build

# Para OpenSearch  
make os-build
```

## 🤔 Por que começar com FAISS e depois migrar para OpenSearch?

### FAISS: Simplicidade e Validação Inicial
FAISS (Facebook AI Similarity Search) é uma biblioteca leve e eficiente para busca vetorial local. Ele é ideal para a fase inicial do projeto porque:
- **Validação rápida**: Permite testar embeddings, pipelines e a API sem necessidade de infraestrutura complexa.
- **Desempenho local**: Funciona diretamente em memória, com alta performance para conjuntos de dados pequenos ou médios.
- **Simplicidade**: Não requer configuração de servidores ou dependências externas, tornando o desenvolvimento mais ágil.

### OpenSearch: Escalabilidade e Produção
OpenSearch é uma solução distribuída e escalável, ideal para ambientes de produção. Ele é recomendado quando:
- **Escalabilidade**: Você precisa lidar com milhões de documentos ou múltiplos usuários simultâneos.
- **Distribuição**: Suporta clusters distribuídos, com réplicas e alta disponibilidade.
- **Funcionalidades avançadas**: Oferece suporte a filtros, busca híbrida (BM25 + kNN), e integração com dashboards para análise.

### Estratégia Incremental
1. **FAISS primeiro**: Comece validando o sistema com dados dummy e FAISS. Isso garante que os embeddings, pipelines e a API estão funcionando corretamente.
2. **Migre para OpenSearch**: Quando estiver pronto para escalar ou integrar dados reais, altere o backend para OpenSearch no `.env` e siga os passos de configuração.

Essa abordagem incremental reduz a complexidade inicial, permitindo que você foque no desenvolvimento do MVP antes de lidar com a infraestrutura distribuída. Assim, você valida o sistema localmente com FAISS e, quando necessário, escala para OpenSearch sem refazer o trabalho.

## 📄 Licença

MIT License - veja LICENSE para detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a seção [Troubleshooting](#-troubleshooting)
2. Consulte logs da aplicação
3. Execute testes para diagnóstico: `make test`
4. Abra issue no repositório

**Desenvolvido para acelerar projetos de RAG jurídico** 🚀