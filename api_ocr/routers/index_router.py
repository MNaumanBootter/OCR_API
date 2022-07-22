from fastapi import APIRouter
from schemas import IndexOut

router = APIRouter()

# index end point for checking if it is working
@router.get("/", response_model=IndexOut)
def index():

    response: IndexOut = IndexOut(message="Working.")
    return response