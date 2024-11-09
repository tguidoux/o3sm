import uuid
from unittest.mock import patch

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import User, UserCreate
from app.tests.utils.utils import random_email, random_lower_string
from fastapi.testclient import TestClient
from sqlmodel import Session, select


def test_create_credential(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"
    data: dict[str, str] = dict()
    r = client.post(
        f"{settings.API_V1_STR}/credentials/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    created_credential: dict[str, str] = r.json()
    # {"access_key":"S-z81wsEL8ng30_9nK8ywxR524LH1lMZJDQpy6qsZpk","secret_key":"jaAv0nNNtowRWAH6WDn8ljwvGxGQKY9H9sLkgoZSYAA","id":"6f8ac332-bd0a-4af7-9370-d8c72241e008","owner_id":"9681149e-e067-4921-b976-d217d3d98a96"}
    assert created_credential.get("access_key")
    assert created_credential.get("secret_key")
    assert created_credential.get("id")
    assert created_credential.get("owner_id") == str(owner.id)


def test_read_credentials(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"
    r = client.get(
        f"{settings.API_V1_STR}/credentials/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    credentials = r.json()
    assert "data" in credentials
    assert "count" in credentials


def test_read_credential(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"
    credential = crud.create_credential(
        session=db,
        owner=owner,
    )
    r = client.get(
        f"{settings.API_V1_STR}/credentials/{credential.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    db_credential: dict[str, str] = r.json()
    assert db_credential.get("id") == str(credential.id)
    assert db_credential.get("owner_id") == str(owner.id)


def test_read_credential_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/credentials/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404, "The response status code must be 404 Not Found"
    assert r.json()["detail"] == "Credential not found"


def test_delete_credential(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"
    credential = crud.create_credential(
        session=db,
        owner=owner,
    )
    r = client.delete(
        f"{settings.API_V1_STR}/credentials/{credential.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    deleted_credential: dict[str, str] = r.json()
    assert deleted_credential.get("message") == "Credential deleted successfully"


def test_delete_credential_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/credentials/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404, "The response status code must be 404 Not Found"
    assert r.json()["detail"] == "Credential not found"
