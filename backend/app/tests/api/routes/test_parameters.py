from unittest.mock import patch

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import ParameterCreate, User
from app.tests.utils.utils import random_email, random_lower_string
from app.utils import generate_password_reset_token
from fastapi.testclient import TestClient
from sqlmodel import Session, select


def test_create_parameter(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    parameter_name: str = random_lower_string()
    assert owner is not None, "The superuser must exist in the database"
    data: dict[str, str] = dict(
        Name=parameter_name,
        Value="Test",
        Type="String",
    )
    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    created_parameter: dict[str, str] = r.json()
    # {"Name":"param2","Value":"value1","Type":"string","Version":1,"DataType":"text","ARN":"arn:o3sm:ssm:::parameter/param2","LastModifiedDate":1731176446}
    assert (
        created_parameter.get("Name") == parameter_name
    ), "The parameter name must be 'Test'"
    assert (
        created_parameter.get("Value") == "Test"
    ), "The parameter value must be 'Test'"
    assert (
        created_parameter.get("Type") == "String"
    ), "The parameter type must be 'String'"
    assert (
        created_parameter.get("Version")
        and isinstance(created_parameter["Version"], int)
        and created_parameter["Version"] == 1
    ), "The parameter version must be 1"
    assert (
        created_parameter.get("DataType") == "text"
    ), "The parameter data type must be 'text'"
    assert (
        created_parameter.get("ARN") == f"arn:o3sm:ssm:::parameter/{parameter_name}"
    ), f"The parameter ARN must be 'arn:o3sm:ssm:::parameter/{parameter_name}'"
    assert created_parameter.get("LastModifiedDate")


def test_read_parameters(
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
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    parameters = r.json()
    assert "data" in parameters
    assert "count" in parameters


def test_read_parameter(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"

    parameter_name: str = random_lower_string()

    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=dict(
            Name=parameter_name,
            Value="Test",
            Type="String",
        ),
    )

    assert r.status_code == 200, "The response status code must be 200 OK"

    r = client.get(
        f"{settings.API_V1_STR}/parameters/{parameter_name}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    db_parameter: dict[str, str] = r.json()
    assert db_parameter.get("Name") == parameter_name
    assert db_parameter.get("Value") == "Test"
    assert db_parameter.get("Type") == "String"
    assert (
        db_parameter.get("Version")
        and isinstance(db_parameter["Version"], int)
        and db_parameter["Version"] == 1
    )
    assert db_parameter.get("DataType") == "text"
    assert db_parameter.get("ARN") == f"arn:o3sm:ssm:::parameter/{parameter_name}"
    assert db_parameter.get("LastModifiedDate")


def test_read_parameter_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/parameters/{random_lower_string()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404, "The response status code must be 404 Not Found"
    assert r.json()["detail"] == "Parameter not found"


def test_read_parameter_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert user is not None, "The superuser must exist in the database"

    parameter_name: str = random_lower_string()

    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=dict(
            Name=parameter_name,
            Value="Test",
            Type="String",
        ),
    )

    assert r.status_code == 200, "The response status code must be 200 OK"

    r = client.get(
        f"{settings.API_V1_STR}/parameters/{parameter_name}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 400, "The response status code must be 400 Bad Request"
    assert r.json()["detail"] == "Not enough permissions"


def test_update_parameter(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"
    parameter_name: str = random_lower_string()

    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=dict(
            Name=parameter_name,
            Value="Test",
            Type="String",
        ),
    )

    assert r.status_code == 200, "The response status code must be 200 OK"

    data = r.json()
    data["Value"] = "Test2"
    r = client.put(
        f"{settings.API_V1_STR}/parameters/{parameter_name}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200, f"The response status code must be 200 OK"

    db_parameter: dict[str, str] = r.json()
    assert db_parameter.get("Name") == parameter_name
    assert db_parameter.get("Value") == "Test2"
    assert db_parameter.get("Type") == "String"
    assert (
        db_parameter.get("Version")
        and isinstance(db_parameter["Version"], int)
        and db_parameter["Version"] == 2
    )
    assert db_parameter.get("DataType") == "text"
    assert db_parameter.get("ARN") == f"arn:o3sm:ssm:::parameter/{parameter_name}"
    assert db_parameter.get("LastModifiedDate")


def test_update_parameter_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:

    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"
    parameter_name: str = random_lower_string()

    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=dict(
            Name=parameter_name,
            Value="Test",
            Type="String",
        ),
    )

    assert r.status_code == 200, "The response status code must be 200 OK"

    r = client.put(
        f"{settings.API_V1_STR}/parameters/{random_lower_string()}",
        headers=superuser_token_headers,
        json=r.json(),
    )
    assert r.status_code == 404, "The response status code must be 404 Not Found"
    assert r.json()["detail"] == "Parameter not found"


def test_update_parameter_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert user is not None, "The superuser must exist in the database"

    parameter_name: str = random_lower_string()

    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=dict(
            Name=parameter_name,
            Value="Test",
            Type="String",
        ),
    )

    assert r.status_code == 200, "The response status code must be 200 OK"

    r = client.put(
        f"{settings.API_V1_STR}/parameters/{parameter_name}",
        headers=normal_user_token_headers,
        json=r.json(),
    )
    assert r.status_code == 400, "The response status code must be 400 Bad Request"
    assert r.json()["detail"] == "Not enough permissions"


def test_delete_parameter(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    owner: User | None = crud.get_user_by_email(
        session=db,
        email=settings.FIRST_SUPERUSER,
    )
    assert owner is not None, "The superuser must exist in the database"
    parameter_name: str = random_lower_string()

    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=dict(
            Name=parameter_name,
            Value="Test",
            Type="String",
        ),
    )

    assert r.status_code == 200, "The response status code must be 200 OK"

    r = client.delete(
        f"{settings.API_V1_STR}/parameters/{parameter_name}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200, "The response status code must be 200 OK"
    assert r.json() == {"message": "Parameter deleted successfully"}


def test_delete_parameter_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/parameters/{random_lower_string()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404, "The response status code must be 404 Not Found"
    assert r.json()["detail"] == "Parameter not found"


def test_delete_parameter_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert user is not None, "The superuser must exist in the database"

    parameter_name: str = random_lower_string()

    r = client.post(
        f"{settings.API_V1_STR}/parameters/",
        headers=superuser_token_headers,
        json=dict(
            Name=parameter_name,
            Value="Test",
            Type="String",
        ),
    )

    assert r.status_code == 200, "The response status code must be 200 OK"

    r = client.delete(
        f"{settings.API_V1_STR}/parameters/{parameter_name}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 400, "The response status code must be 400 Bad Request"
    assert r.json()["detail"] == "Not enough permissions"
