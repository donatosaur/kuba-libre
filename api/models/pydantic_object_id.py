# Modified:    2021-08-20
# Description: Implements a validator for BSON object IDs
#              (see https://pydantic-docs.helpmanual.io/usage/types/#classes-with-__get_validators__)

from bson import ObjectId


class PydanticObjectID(ObjectId):
    """Defines a Pydantic type validator for BSON object IDs"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

    @classmethod
    def validate(cls, oid: ObjectId):
        if not isinstance(oid, ObjectId):
            raise TypeError(f"Unsupported type {oid.__class__}")
        return str(oid)

    def __repr__(self):
        return f"PydanticObjectID{super().__repr__})"
