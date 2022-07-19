from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from auth import auth_handler
from schemas import ScanTextFromImageOut, GetScansOut, GetScanOut
from sqlalchemy.orm import Session
from database import get_db
from models import User
import json
from query import create_file_result, put_image_to_bucket, call_endpoint, get_all_file_results, get_file_result


router = APIRouter()


# this endpoint takes a list of images then uploads them to MinIO, creates new FileResult records in DB
# and finally calls inner API for scanning images and updating the DB with results
@router.post("/scan_text", response_model=ScanTextFromImageOut)
async def scan_text_from_image(images: list[UploadFile], current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):

    file_result_ids = []
    for image in images:
        print(f"File Name: {image.filename}")
        print(f"File Content Type: {image.content_type}")

        # validating the file mime type to png or jpeg
        if(image.content_type not in ["image/png", "image/jpeg"]):
            print("File format not valid.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")

        # uploading file to minIO
        await put_image_to_bucket(image_obj=image)

        # saving file result in db
        file_result_id = await create_file_result(current_user_email, image.filename, db)
        file_result_ids.append(file_result_id)

    # informing ocr_api to start scanning
    await call_endpoint("http://192.168.20.102:8002/start_scanning")

    response: ScanTextFromImageOut = ScanTextFromImageOut(message="Image scanning queued", scan_ids=file_result_ids)
    return response


# get all scans of current user
@router.get("/scans", response_model=GetScansOut)
async def get_scans(current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    file_results = await get_all_file_results(current_user_email, db)
    response: GetScansOut = GetScansOut(results=file_results)
    return response


# get single scan of current user with a scan id (FileResult.id)
@router.get("/scan", response_model=GetScanOut)
async def get_scan(scan_id: int, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    file_result = await get_file_result(scan_id, current_user_email, db)
    response: GetScanOut = GetScanOut(result=file_result)
    return response