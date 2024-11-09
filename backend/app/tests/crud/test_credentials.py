from app import crud
from app.models import UserCreate
from app.tests.utils.utils import random_email, random_lower_string
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session


def test_get_credential_by_access_key(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    credential = crud.create_credential(session=db, owner=user)
    credential_2 = crud.get_credential_by_access_key(
        session=db, access_key=credential.access_key
    )

    assert credential
    assert credential_2
    assert user
    assert credential.access_key == credential_2.access_key
    assert credential.secret_key == credential_2.secret_key
    assert credential.owner_id == credential_2.owner_id
    assert credential.owner
    assert credential_2.owner
    assert credential.owner.id == credential_2.owner.id
    assert jsonable_encoder(credential) == jsonable_encoder(credential_2)


def test_get_credential_by_access_key_none(db: Session) -> None:
    credential = crud.get_credential_by_access_key(session=db, access_key="")
    assert credential is None


def test_create_credential(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    credential = crud.create_credential(session=db, owner=user)
    assert credential.access_key
    assert credential.secret_key
    assert credential.owner_id == user.id
    assert credential.owner
