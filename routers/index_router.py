from fastapi import APIRouter

router = APIRouter()

# index end point for checking if it is working
@router.get("/")
def index():
    return {"message": "Working."}