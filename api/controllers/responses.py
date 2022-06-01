# Modified:    2021-08-26
# Description: Define custom JSON encoder for JSON responses
#
import json
from bson import ObjectId
from typing import Any
from fastapi.responses import JSONResponse
from marble_game import MarbleGame, MarbleGameEncoder
from models.pydantic_object_id import PydanticObjectID


class CustomJSONResponse(JSONResponse):
    """Extends JSONResponse so that custom objects are encoded correctly"""

    # override the default json encoder
    def render(self, content: Any) -> bytes:
        # generally, FastAPI will call dict() on the pydantic model
        if isinstance(content, dict):
            for k, v in content.items():
                # ObjectId -> str
                if isinstance(v, (ObjectId, PydanticObjectID)):
                    content[k] = str(v)
                # MarbleGame -> dict
                elif isinstance(v, MarbleGame):
                    content[k] = json.dumps(v, cls=MarbleGameEncoder)
        elif isinstance(content, list):
            for d in content:
                for k, v in d.items():
                    # ObjectId -> str
                    if isinstance(v, (ObjectId, PydanticObjectID)):
                        d[k] = str(v)
                    # MarbleGame -> dict
                    elif isinstance(v, MarbleGame):
                        d[k] = json.dumps(v, cls=MarbleGameEncoder)
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
