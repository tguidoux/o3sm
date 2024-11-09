from app import crud
from app.models import ParameterCreate, UserCreate
from app.tests.utils.utils import random_email, random_lower_string
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session


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
