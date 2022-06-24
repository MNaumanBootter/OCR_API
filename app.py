from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from email_validator import validate_email, EmailNotValidError
from database import engine, get_db, Base
from schemas import AuthDetails
from requests import Session
from auth import AuthHandler
from config import settings
from models import User
import uvicorn
import easyocr
import shutil


# declaring FastAPI app
app = FastAPI()

# authentication handler
auth_handler = AuthHandler()

# create all tables for first time
Base.metadata.create_all(bind=engine)


# index end point for checking if it is working
@app.get("/")
def index():
    return {"message": "Working."}


@app.post("/signup", status_code=201)
def signup(auth_details: AuthDetails, db: Session = Depends(get_db)):
    try:
        email = validate_email(email).email
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


@app.post("/login")
def login(auth_details: AuthDetails, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == auth_details.email).first()

    if (user is None) or (not auth_handler.verify_password(auth_details.password, user.password)):
        raise HTTPException(status_code=401, detail="Invalid email and/or password")

    token = auth_handler.encode_token(user.email)

    return {"token": token}


# this endpoint takes an image and returns the english text extracted by OCR
@app.post("/scan_text", dependencies=[Depends(auth_handler.auth_wrapper)])
async def scan_text_from_image(image: UploadFile = File(...)):

    print(f"File Name: {image.filename}")
    print(f"File Content Type: {image.content_type}")

    # checking if the file content is image
    if(image.content_type not in ["image/png", "image/jpeg"]):
        print("File format not accessable.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")

    # path to store images
    destination_file_path = "./images/"+image.filename

    # saving images
    with open(destination_file_path, "wb") as image_buffer:
        shutil.copyfileobj(image.file, image_buffer)

    # scanning image by OCR package
    ocr_reader = easyocr.Reader(['en'], gpu=False)
    ocr_result = ocr_reader.readtext(destination_file_path)
    ocr_result_text = [text for (bbox, text, prob) in ocr_result]

    print(f"File scanned successfully.")

    return {"filename": image.filename, "result": ocr_result_text}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
