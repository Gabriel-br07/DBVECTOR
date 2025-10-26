.PHONY: install install-dev clean shell add add-dev update format lint demo
.PHONY: faiss-build faiss-query os-up os-down os-logs os-build os-query api test test-cov data-merge

# Instalação
install:
	poetry install

install-dev: install
	poetry install --with dev

# Limpeza
clean:
	rm -rf data/indexes/faiss/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	poetry env info --path | xargs rm -rf

# Ambiente virtual
shell:
	poetry shell

# Dependências
add:
	poetry add $(package)

add-dev:
	poetry add --group dev $(package)

update:
	poetry update

# Linting e formatação
format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

lint:
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/
	poetry run flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

# Testes
test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# FAISS workflows
faiss-build:
	poetry run python -m src.pipelines.build_faiss

faiss-query:
	poetry run python -m src.pipelines.query_faiss

# OpenSearch workflows
os-up:
	docker-compose up -d opensearch

os-down:
	docker-compose down -v

os-logs:
	docker-compose logs -f opensearch

os-build:
	poetry run python -m src.pipelines.build_opensearch

os-query:
	poetry run python -m src.pipelines.query_opensearch

# API
api:
	poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Workflow completo FAISS
setup-faiss: install faiss-build
	@echo "✅ Setup FAISS completo! Execute 'make api' para iniciar a API"

# Workflow completo OpenSearch  
setup-opensearch: install os-up
	@echo "⏳ Aguardando OpenSearch inicializar..."
	@sleep 15
	$(MAKE) os-build
	@echo "✅ Setup OpenSearch completo! Altere SEARCH_BACKEND=opensearch no .env"

# Demo rápido
demo:
	poetry run python demo.py

# Consolidação de dados
data-merge:
	poetry run python -m src.tools.tratamento_dados --input data --output data/merged_clean.jsonl --dedupe-by id