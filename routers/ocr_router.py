from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from auth import auth_handler
from schemas import OcrFileResult, ScanTextFromImageOut
import easyocr
import shutil
from sqlalchemy.orm import Session
from database import get_db
from models import User, FileResult
from query import get_user_id_by_email, create_file_result


router = APIRouter()

# initializing OCR reader
ocr_reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=r"ocr_models")

# this endpoint takes an image and returns the english text extracted by OCR
@router.post("/scan_text", response_model=ScanTextFromImageOut)
async def scan_text_from_image(images: list[UploadFile], current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):

    multiple_file_results: list[OcrFileResult] = []

    for image in images:
        print(f"File Name: {image.filename}")
        print(f"File Content Type: {image.content_type}")

        # validating the file mime type to png or jpeg
        if(image.content_type not in ["image/png", "image/jpeg"]):
            print("File format not valid.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")

        # path to store images
        file_save_path = "./images/"+image.filename

        # saving images
        with open(file_save_path, "wb") as image_buffer:
            shutil.copyfileobj(image.file, image_buffer)

        # scanning image by OCR reader
        ocr_result = ocr_reader.readtext(file_save_path, detail=0)

        # getting current user's id
        user_id = await get_user_id_by_email(current_user_email, db)

        # saving file result in db
        file_result_id = await create_file_result(user_id, image.filename, ocr_result, db)

        # append to mutiple file results list for endpoint's response
        multiple_file_results.append(OcrFileResult(id=file_result_id, file_name=image.filename, text_lines=ocr_result))


    print(f"Files scanned successfully.")

    response: ScanTextFromImageOut = ScanTextFromImageOut(result=multiple_file_results)
    return response