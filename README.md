# AI Knowledge Assistant

API REST para upload e gerenciamento de documentos PDF, construída com FastAPI e PostgreSQL. Base para um assistente de IA com RAG (Retrieval-Augmented Generation).

## Stack

- **FastAPI** — framework web com documentação automática (OpenAPI)
- **PostgreSQL 16** — banco de dados relacional
- **SQLAlchemy 2** — ORM com suporte a tipagem moderna
- **Alembic** — migrations de banco de dados
- **Docker + Docker Compose** — containerização
- **pytest + httpx** — testes de integração

## Arquitetura

```
app/
├── api/v1/endpoints/   # rotas HTTP
├── core/               # configurações (env vars)
├── db/                 # models e sessão do banco
├── schemas/            # modelos Pydantic (request/response)
└── services/           # lógica de negócio (armazenamento de arquivos)
migrations/             # migrations Alembic
tests/                  # testes de integração
```

O projeto segue arquitetura em camadas: **API → Service → DB**. Os endpoints não acessam o banco diretamente — passam pelo service layer. A injeção de dependência do FastAPI (`Depends`) é usada para gerenciar a sessão do banco.

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Como rodar

**1. Clone o repositório e configure o ambiente:**

```bash
git clone <url-do-repositorio>
cd ai-knowledge-assistant
cp .env.example .env
```

**2. Suba os containers:**

```bash
docker compose up --build
```

**3. Em outro terminal, aplique as migrations:**

```bash
docker compose exec api alembic upgrade head
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa: `http://localhost:8000/docs`

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Status da API |
| `POST` | `/documents/upload` | Faz upload de um PDF |
| `GET` | `/documents/` | Lista todos os documentos |
| `GET` | `/documents/{id}` | Busca um documento por ID |
| `DELETE` | `/documents/{id}` | Remove um documento |
| `GET` | `/documents/{id}/download` | Baixa o arquivo PDF |

## Variáveis de ambiente

Crie um arquivo `.env` na raiz com base no `.env.example`:

```env
APP_NAME=AI Knowledge Assistant
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_knowledge_assistant

UPLOAD_DIR=uploads
```

## Testes

Os testes usam SQLite em memória — não precisam do Docker rodando.

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Migrations

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Gerar nova migration após alterar um model
alembic revision --autogenerate -m "descricao_da_mudanca"

# Voltar uma migration
alembic downgrade -1

# Ver histórico
alembic history
```
