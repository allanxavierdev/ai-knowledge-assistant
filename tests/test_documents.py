import io
import pytest
from fastapi.testclient import TestClient


# ── helpers ──────────────────────────────────────────────────────────────────

def make_pdf(name: str = "test.pdf") -> dict:
    """Cria um 'PDF' mínimo em memória para usar nos uploads."""
    content = b"%PDF-1.4 fake pdf content"
    return {"file": (name, io.BytesIO(content), "application/pdf")}


def upload_pdf(client: TestClient, name: str = "test.pdf") -> dict:
    """Faz upload e retorna o JSON da resposta."""
    response = client.post("/documents/upload", files=make_pdf(name))
    assert response.status_code == 200
    return response.json()


# ── upload ────────────────────────────────────────────────────────────────────

def test_upload_pdf_success(client, tmp_path, monkeypatch):
    # Redireciona uploads para pasta temporária (não suja o diretório real)
    monkeypatch.setattr("app.core.config.settings.upload_dir", str(tmp_path))

    response = client.post("/documents/upload", files=make_pdf())

    assert response.status_code == 200
    data = response.json()
    assert data["original_name"] == "test.pdf"
    assert data["status"] == "uploaded"
    assert data["size_bytes"] > 0
    assert "id" in data


def test_upload_non_pdf_returns_400(client):
    files = {"file": ("image.png", io.BytesIO(b"fake image"), "image/png")}
    response = client.post("/documents/upload", files=files)

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


# ── listagem ──────────────────────────────────────────────────────────────────

def test_list_documents_empty(client):
    response = client.get("/documents/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_documents_returns_uploaded(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.upload_dir", str(tmp_path))

    upload_pdf(client)
    upload_pdf(client, name="outro.pdf")

    response = client.get("/documents/")

    assert response.status_code == 200
    assert len(response.json()) == 2


# ── busca por id ──────────────────────────────────────────────────────────────

def test_get_document_success(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.upload_dir", str(tmp_path))

    doc = upload_pdf(client)
    response = client.get(f"/documents/{doc['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == doc["id"]


def test_get_document_not_found(client):
    response = client.get("/documents/id-que-nao-existe")

    assert response.status_code == 404


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_document_success(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.upload_dir", str(tmp_path))

    doc = upload_pdf(client)
    response = client.delete(f"/documents/{doc['id']}")

    assert response.status_code == 204

    # Confirma que sumiu do banco
    get_response = client.get(f"/documents/{doc['id']}")
    assert get_response.status_code == 404


def test_delete_document_not_found(client):
    response = client.delete("/documents/id-que-nao-existe")

    assert response.status_code == 404


# ── download ──────────────────────────────────────────────────────────────────

def test_download_document_success(client, tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.upload_dir", str(tmp_path))

    doc = upload_pdf(client)
    response = client.get(f"/documents/{doc['id']}/download")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_download_document_not_found(client):
    response = client.get("/documents/id-que-nao-existe/download")

    assert response.status_code == 404
