# Modified:    2021-08-20
# Description: Implements a controller for player info
#
from fastapi import APIRouter, Body, Request, HTTPException, status
from ..models import PydanticObjectID, player_model
from ..main import app

game_router = APIRouter()
