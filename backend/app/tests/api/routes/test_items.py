import uuid

from app.core.config import settings
from app.tests.utils.item import create_random_credential
from fastapi.testclient import TestClient
from sqlmodel import Session


def test_create_credential(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data: dict[str, str] = dict()
    response = client.post(
        f"{settings.API_V1_STR}/credentials/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["access_key"] != None
    assert content["secret_key"] != None
    assert "id" in content
    assert "owner_id" in content


def test_read_credential(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_credential(db)
    response = client.get(
        f"{settings.API_V1_STR}/credentials/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["access_key"] != None
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


def test_read_credential_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/credentials/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Credential not found"


def test_read_credential_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_credential(db)
    response = client.get(
        f"{settings.API_V1_STR}/credentials/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_credentials(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_credential(db)
    create_random_credential(db)
    response = client.get(
        f"{settings.API_V1_STR}/credentials/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


# # This test is not needed because we don't have an update endpoint
# def test_update_credential(
#     client: TestClient, superuser_token_headers: dict[str, str], db: Session
# ) -> None:
#     item = create_random_credential(db)
#     data = {"title": "Updated title", "description": "Updated description"}
#     response = client.put(
#         f"{settings.API_V1_STR}/credentials/{item.id}",
#         headers=superuser_token_headers,
#         json=data,
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["title"] == data["title"]
#     assert content["description"] == data["description"]
#     assert content["id"] == str(item.id)
#     assert content["owner_id"] == str(item.owner_id)


# def test_update_credential_not_found(
#     client: TestClient, superuser_token_headers: dict[str, str]
# ) -> None:
#     data = {"title": "Updated title", "description": "Updated description"}
#     response = client.put(
#         f"{settings.API_V1_STR}/credentials/{uuid.uuid4()}",
#         headers=superuser_token_headers,
#         json=data,
#     )
#     assert response.status_code == 404
#     content = response.json()
#     assert content["detail"] == "Item not found"


# def test_update_credential_not_enough_permissions(
#     client: TestClient, normal_user_token_headers: dict[str, str], db: Session
# ) -> None:
#     item = create_random_credential(db)
#     data = {"title": "Updated title", "description": "Updated description"}
#     response = client.put(
#         f"{settings.API_V1_STR}/credentials/{item.id}",
#         headers=normal_user_token_headers,
#         json=data,
#     )
#     assert response.status_code == 400
#     content = response.json()
#     assert content["detail"] == "Not enough permissions"


def test_delete_credential(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_credential(db)
    response = client.delete(
        f"{settings.API_V1_STR}/credentials/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Credential deleted successfully"


def test_delete_credential_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/credentials/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Credential not found"


def test_delete_credential_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_credential(db)
    response = client.delete(
        f"{settings.API_V1_STR}/credentials/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"
