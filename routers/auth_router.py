from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, Depends, APIRouter
from schemas import SignupIn, SignupOut, LoginIn, LoginOut
from requests import Session
from auth import auth_handler
from database import get_db
from models import User

router = APIRouter()


@router.post("/signup", status_code=201, response_model=SignupOut, response_model_exclude_unset=True)
def signup(auth_details: SignupIn, db: Session = Depends(get_db)):
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

    response: SignupOut = new_user
    return response


@router.post("/login", response_model=LoginOut)
def login(auth_details: LoginIn, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == auth_details.email).first()

    if (user is None) or (not auth_handler.verify_password(auth_details.password, user.password)):
        raise HTTPException(status_code=401, detail="Invalid email and/or password")

    token = auth_handler.encode_token(user.email)

    response: LoginOut = {"token": token}
    return response