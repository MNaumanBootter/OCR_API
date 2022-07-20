from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from auth import auth_handler
from schemas import ScanImageOut, GetScansOut, GetScanOut, ScanVideoOut
from sqlalchemy.orm import Session
from database import get_db
from models import User
from video_to_image import convert_video_to_images
from query import create_file_result, put_image_to_bucket, call_endpoint, get_all_file_results, get_file_result, put_video_image_to_bucket


router = APIRouter()


# this endpoint takes a list of images then uploads them to MinIO, creates new FileResult records in DB
# and finally calls inner API for scanning images and updating the DB with results
@router.post("/scan_image", response_model=ScanImageOut)
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

    response: ScanImageOut = ScanImageOut(message="Image scanning queued", scan_ids=file_result_ids)
    return response

@router.post("/scan_video", response_model=ScanVideoOut)
async def scan_text_from_image(video: UploadFile, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):

    file_result_ids = []
    print(f"File Name: {video.filename}")
    print(f"File Content Type: {video.content_type}")

    if(video.content_type not in ["video/mp4"]):
            print("Video format not valid.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video type.")

    images = await convert_video_to_images(video.file)
    for image_index, image in enumerate(images):
        image_filename = f"{video.filename}_{image_index}.jpg"
        # uploading file to minIO
        await put_video_image_to_bucket(image_ndarrray=image, image_filename=image_filename)

        # saving file result in db
        file_result_id = await create_file_result(current_user_email, image_filename, db)
        file_result_ids.append(file_result_id)

        # informing ocr_api to start scanning
        await call_endpoint("http://192.168.20.102:8002/start_scanning")
        # break

    response: ScanVideoOut = ScanVideoOut(message="under construction", scan_ids=[])
    return response


# get all scans of current user
@router.get("/scans", response_model=GetScansOut)
async def get_scans(skip: int = 0, limit: int = 10, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    file_results = await get_all_file_results(skip, limit, current_user_email, db)
    response: GetScansOut = GetScansOut(results=file_results)
    return response


# get single scan of current user with a scan id (FileResult.id)
@router.get("/scan", response_model=GetScanOut)
async def get_scan(scan_id: int, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    file_result = await get_file_result(scan_id, current_user_email, db)
    if not file_result:
        raise HTTPException(status_code=404, detail="Scan not found")

    response: GetScanOut = GetScanOut(result=file_result)
    return response