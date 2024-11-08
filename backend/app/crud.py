import secrets
from typing import Any, Tuple

from app.core.security import get_password_hash, verify_password
from app.models import (
    Credential,
    Parameter,
    ParameterCreate,
    User,
    UserCreate,
    UserUpdate,
)
from app.utils import get_date_str
from sqlmodel import Session, select


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def get_credential_by_access_key(
    *, session: Session, access_key: str
) -> Credential | None:
    statement = select(Credential).where(Credential.access_key == access_key)
    credential = session.exec(statement).first()
    return credential


def create_credential(*, session: Session, owner: User) -> Tuple[Credential, str]:
    access_key = secrets.token_urlsafe(32)
    secret_key = secrets.token_urlsafe(32)
    hashed_secret_key = get_password_hash(secret_key)

    credential = Credential(
        access_key=access_key,
        secret_key=hashed_secret_key,
        owner_id=owner.id,
        owner=owner,
    )

    db_credential = Credential.model_validate(credential, update={"owner_id": owner.id})
    session.add(db_credential)
    session.commit()
    session.refresh(db_credential)
    return db_credential, secret_key


def get_parameter_by_name(*, session: Session, name: str) -> Parameter | None:
    statement = select(Parameter).where(Parameter.name == name)
    parameter = session.exec(statement).first()
    return parameter


def create_parameter(
    *,
    session: Session,
    parameter_in: ParameterCreate,
    owner: User,
) -> Parameter:

    last_modified_date: str = get_date_str()

    parameter = Parameter(
        name=parameter_in.name,
        value=parameter_in.value,
        owner_id=owner.id,
        owner=owner,
        last_modified_date="",
        type=parameter_in.type or "string",
        data_type=parameter_in.data_type or "text",
    )

    db_parameter = Parameter.model_validate(
        parameter,
        update={
            "owner_id": owner.id,
            "last_modified_date": last_modified_date,
        },
    )
    session.add(db_parameter)
    session.commit()
    session.refresh(db_parameter)
    return db_parameter
