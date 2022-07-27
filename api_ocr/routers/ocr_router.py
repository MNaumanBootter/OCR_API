from fastapi import APIRouter, UploadFile, status, HTTPException, Depends, Body
from celery_tasks import scan_image
from background_tasks import scan_image_batch
from schemas import StartScanningOut
from sqlalchemy.orm import Session
from database import get_db
import time
from query import create_image_scan, put_image_to_bucket


router = APIRouter()


# this endpoint starts ocr scanning through a celery task
@router.get("/start_scanning", response_model=StartScanningOut)
async def scan_text_from_image():
    scan_image.delay()
    response: StartScanningOut = StartScanningOut(message="Scanning started", status=1)
    return response


@router.post("/start_batch_scanning", response_model=StartScanningOut)
# async def start_batch_scanning(video_id: int = Body(), user_id: int = Body()):
async def start_batch_scanning():

    # status = await scan_image_batch(video_id, user_id)
    print("started batch scanning")
    print(time.ctime())
    status = await scan_image_batch()

    if status:
        response: StartScanningOut = StartScanningOut(message="Scanning started", status=1)
    else:
        response: StartScanningOut = StartScanningOut(message="No unscanned record found", status=0)

    return response


@router.post("/scan_images", response_model=StartScanningOut)
async def scan_images(images: list[UploadFile], user_id: int, db: Session = Depends(get_db)):
    for image in images:

        if(image.content_type not in ["image/png", "image/jpeg"]):
                print("File format not valid.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")

        # uploading file to minIO
        await put_image_to_bucket(image_obj=image)

        # saving file result in db
        file_scan_id = await create_image_scan(user_id, image.filename, db)

    scan_image.delay()
    response: StartScanningOut = StartScanningOut(message="Scanning started")
    return response