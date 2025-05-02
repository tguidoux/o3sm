from app import crud
from app.models import Credential
from app.tests.utils.user import create_random_user
from sqlmodel import Session


def create_random_credential(db: Session) -> Credential:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    return crud.create_credential(session=db, owner=user)
