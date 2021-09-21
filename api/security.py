# Modified:    2021-08-26
# Description: Implements authentication for the database0
#
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from .config import settings

# Define OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Define JWT encoding and decoding
def jwt_encode(payload: dict) -> str:
    """
    Encodes the payload to a JSON Web Token

    :param payload: JWT claims to be encoded
    :return: JSON web token
    """
    # add expiration datetime to the payload and cast any BSON ObjectIDs to str
    payload.update({
        "sub": str(payload.get("sub")),
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    })
    return jwt.encode(payload, settings.SECRET_KEY, settings.JWT_ALGORITHM)


def jwt_decode(token: str) -> dict:
    """
    Decodes the JSON web token to its claims

    :param token: JSON Web Token to be decoded
    :return: the token's payload
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
