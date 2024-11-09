from app import crud
from app.core.security import verify_password
from app.models import ParameterCreate, User, UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

#
# def test_create_user(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password)
#     user = crud.create_user(session=db, user_create=user_in)
#     assert user.email == email
#     assert hasattr(user, "hashed_password")
#
#
# def test_authenticate_user(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password)
#     user = crud.create_user(session=db, user_create=user_in)
#     authenticated_user = crud.authenticate(session=db, email=email, password=password)
#     assert authenticated_user
#     assert user.email == authenticated_user.email
#
#
# def test_not_authenticate_user(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user = crud.authenticate(session=db, email=email, password=password)
#     assert user is None
#
#
# def test_check_if_user_is_active(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password)
#     user = crud.create_user(session=db, user_create=user_in)
#     assert user.is_active is True
#
#
# def test_check_if_user_is_active_inactive(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password, disabled=True)
#     user = crud.create_user(session=db, user_create=user_in)
#     assert user.is_active
#
#
# def test_check_if_user_is_superuser(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password, is_superuser=True)
#     user = crud.create_user(session=db, user_create=user_in)
#     assert user.is_superuser is True
#
#
# def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
#     username = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=username, password=password)
#     user = crud.create_user(session=db, user_create=user_in)
#     assert user.is_superuser is False
#
#
# def test_get_user(db: Session) -> None:
#     password = random_lower_string()
#     username = random_email()
#     user_in = UserCreate(email=username, password=password, is_superuser=True)
#     user = crud.create_user(session=db, user_create=user_in)
#     user_2 = db.get(User, user.id)
#     assert user_2
#     assert user.email == user_2.email
#     assert jsonable_encoder(user) == jsonable_encoder(user_2)
#
#
# def test_update_user(db: Session) -> None:
#     password = random_lower_string()
#     email = random_email()
#     user_in = UserCreate(email=email, password=password, is_superuser=True)
#     user = crud.create_user(session=db, user_create=user_in)
#     new_password = random_lower_string()
#     user_in_update = UserUpdate(password=new_password, is_superuser=True)
#     if user.id is not None:
#         crud.update_user(session=db, db_user=user, user_in=user_in_update)
#     user_2 = db.get(User, user.id)
#     assert user_2
#     assert user.email == user_2.email
#     assert verify_password(new_password, user_2.hashed_password)
#


# def test_get_credential_by_access_key(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password)
#     user = crud.create_user(session=db, user_create=user_in)
#     credential = crud.create_credential(session=db, owner=user)
#     credential_2 = crud.get_credential_by_access_key(
#         session=db, access_key=credential.access_key
#     )
#
#     assert credential
#     assert credential_2
#     assert user
#     assert credential.access_key == credential_2.access_key
#     assert credential.secret_key == credential_2.secret_key
#     assert credential.owner_id == credential_2.owner_id
#     assert credential.owner
#     assert credential_2.owner
#     assert credential.owner.id == credential_2.owner.id
#     assert jsonable_encoder(credential) == jsonable_encoder(credential_2)
#
#
# def test_get_credential_by_access_key_none(db: Session) -> None:
#     credential = crud.get_credential_by_access_key(session=db, access_key="")
#     assert credential is None
#
#
# def test_create_credential(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password)
#     user = crud.create_user(session=db, user_create=user_in)
#     credential = crud.create_credential(session=db, owner=user)
#     assert credential.access_key
#     assert credential.secret_key
#     assert credential.owner_id == user.id
#     assert credential.owner


def test_create_parameter(db: Session) -> None:
    user_in = UserCreate(email=random_email(), password=random_lower_string())
    parameter_name: str = random_lower_string()
    parameter_in = ParameterCreate(
        Name=parameter_name,
        Value="test",
        Type="string",
    )
    user = crud.create_user(session=db, user_create=user_in)
    parameter = crud.create_parameter(session=db, owner=user, parameter_in=parameter_in)
    assert parameter
    assert parameter.owner_id == user.id
    assert parameter.owner
    assert parameter.owner.id == user.id
    assert parameter.Name == parameter_name
    assert parameter.Value == "test"
    assert parameter.Type == "string"
    assert parameter.DataType == "text"
    assert parameter.Version == 1
    assert parameter.ARN == f"arn:o3sm:ssm:::parameter/{parameter_name}"


def test_get_parameter_by_name(db: Session) -> None:
    user_in = UserCreate(email=random_email(), password=random_lower_string())
    parameter_name: str = random_lower_string()
    parameter_in = ParameterCreate(
        Name=parameter_name,
        Value="test",
        Type="string",
    )
    user = crud.create_user(session=db, user_create=user_in)
    parameter = crud.create_parameter(session=db, owner=user, parameter_in=parameter_in)
    parameter_2 = crud.get_parameter_by_name(session=db, name=parameter_name)
    assert parameter
    assert parameter_2
    assert parameter.Name == parameter_2.Name
    assert parameter.Value == parameter_2.Value
    assert parameter.Type == parameter_2.Type
    assert parameter.DataType == parameter_2.DataType
    assert parameter.Version == parameter_2.Version
    assert parameter.ARN == parameter_2.ARN
    assert parameter.owner_id == parameter_2.owner_id
    assert parameter.owner
    assert parameter_2.owner
    assert parameter.owner.id == parameter_2.owner.id
    assert jsonable_encoder(parameter) == jsonable_encoder(parameter_2)
