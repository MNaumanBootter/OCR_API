
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, Depends, APIRouter
from schemas import AuthDetails
from requests import Session
from auth import auth_handler
from database import get_db
from models import User

router = APIRouter()


@router.post("/signup", status_code=201)
def signup(auth_details: AuthDetails, db: Session = Depends(get_db)):
    try:
        email = validate_email(auth_details.email).email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Email not valid")

    db_user = db.query(User).filter(User.email == auth_details.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=auth_details.email, password=auth_handler.get_password_hash(auth_details.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"user": new_user}


@router.post("/login")
def login(auth_details: AuthDetails, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == auth_details.email).first()

    if (user is None) or (not auth_handler.verify_password(auth_details.password, user.password)):
        raise HTTPException(status_code=401, detail="Invalid email and/or password")

    token = auth_handler.encode_token(user.email)

    return {"token": token}