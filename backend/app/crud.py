import logging
import os
import secrets
from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.core.security import get_password_hash, verify_password
from app.models import (
    Credential,
    Parameter,
    ParameterCreate,
    ParameterUpdate,
    User,
    UserCreate,
    UserUpdate,
)
from app.utils import get_date_timestamp
from cryptography.fernet import Fernet
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, func, select


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
    *,
    session: Session,
    access_key: str,
) -> Credential | None:
    statement = select(Credential).where(Credential.access_key == access_key)
    credential = session.exec(statement).first()
    return credential


def create_credential(
    *,
    session: Session,
    owner: User,
) -> Credential:
    access_key = secrets.token_urlsafe(32)
    secret_key = secrets.token_urlsafe(32)

    credential = Credential(
        access_key=access_key,
        secret_key=secret_key,
        owner_id=owner.id,
        owner=owner,
    )

    db_credential = Credential.model_validate(credential, update={"owner_id": owner.id})
    session.add(db_credential)
    session.commit()
    session.refresh(db_credential)
    return db_credential


def get_parameter_by_name(
    *,
    session: Session,
    name: str,
    secret_key: str = "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM=",
    with_decryption: bool = False,
) -> Parameter | None:
    statement = select(Parameter).where(Parameter.Name == name)
    parameter = session.exec(statement).first()

    if parameter and parameter.Type == "SecureString" and with_decryption:
        try:
            parameter.Value = (
                Fernet(secret_key).decrypt(parameter.Value.encode()).decode()
            )
        except Exception:
            logging.error(f"Failed to decrypt parameter {name}")

    return parameter


def create_parameter(
    *,
    session: Session,
    parameter_in: ParameterCreate,
    owner: User,
    secret_key: str = "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM=",
) -> Parameter:
    last_modified_date: int = get_date_timestamp()
    arn: str = f"arn:o3sm:ssm:::parameter/{parameter_in.Name}"
    parameter_type: str = parameter_in.Type or "String"
    parameter_data_type: str = parameter_in.DataType or "text"
    parameter_value: str = parameter_in.Value

    if parameter_type == "SecureString":
        try:
            parameter_value = (
                Fernet(secret_key).encrypt(parameter_value.encode()).decode()
            )
        except Exception:
            logging.error(f"Failed to encrypt parameter {parameter_in.Name}")

    parameter = Parameter(
        Name=parameter_in.Name,
        Value=parameter_value,
        owner_id=owner.id,
        owner=owner,
        LastModifiedDate=last_modified_date,
        Type=parameter_type,
        DataType=parameter_data_type,
        ARN=arn,
    )

    db_parameter = Parameter.model_validate(
        parameter,
        update={
            "owner_id": owner.id,
        },
    )
    session.add(db_parameter)
    session.commit()
    session.refresh(db_parameter)
    return db_parameter


def read_parameters(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    with_decryption: bool = False,
    secret_key: str = "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM=",
) -> tuple[list[Parameter], int]:
    """
    Retrieve parameters.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Parameter)
        count = session.exec(count_statement).one()
        statement = select(Parameter).offset(skip).limit(limit)
        parameters = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Parameter)
            .where(Parameter.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Parameter)
            .where(Parameter.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        parameters = session.exec(statement).all()

    if with_decryption:
        for parameter in parameters:
            if parameter.Type == "SecureString":
                try:
                    parameter.Value = (
                        Fernet(secret_key).decrypt(parameter.Value.encode()).decode()
                    )
                except Exception:
                    logging.error(f"Failed to decrypt parameter {parameter.Name}")

    return parameters, count


def update_parameter(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    name: str,
    parameter_in: ParameterUpdate,
    secret_key: str = "TkUTrhRhJ1-PRfIBiOA7OJrcSnxaMugEvdwAnyNXdCM=",
) -> Parameter:
    """
    Update a parameter.
    """
    parameter = get_parameter_by_name(
        session=session,
        name=name,
        secret_key=secret_key,
    )
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    if not current_user.is_superuser and (parameter.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_dict = parameter_in.model_dump(exclude_unset=True)
    update_dict["LastModifiedDate"] = get_date_timestamp()

    # Make sure we don't update the name or arn as they are unique
    update_dict.pop("Name", None)
    update_dict.pop("ARN", None)
    update_dict["Version"] = parameter.Version + 1

    parameter.sqlmodel_update(update_dict)

    unencrypted_value: str = parameter.Value
    if parameter.Type == "SecureString":
        try:
            parameter.Value = (
                Fernet(secret_key).encrypt(parameter.Value.encode()).decode()
            )
        except Exception:
            logging.error(f"Failed to encrypt parameter {name}")

    session.add(parameter)
    session.commit()
    session.refresh(parameter)

    if parameter.Type == "SecureString":
        parameter.Value = unencrypted_value

    return parameter
