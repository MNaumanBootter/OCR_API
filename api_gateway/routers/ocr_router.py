from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, BackgroundTasks, Body
from background_tasks import call_videos_api, timeloop_app
from auth import auth_handler
from schemas import ScanImageOut, GetImageScansOut, GetScanOut, ScanVideoOut, GetVideoScansOut, GetVideoScanOut, StartScanningOut
from sqlalchemy.orm import Session
from database import get_db
from models import User
from query import create_image_scan, put_image_to_bucket, get_user_id_by_email, get_all_image_results, get_image_result, get_all_videos, get_video


router = APIRouter()


# this endpoint takes a list of images then uploads them to MinIO, creates new FileResult records in DB
# and finally calls inner API for scanning images and updating the DB with results
@router.post("/scan_images", response_model=ScanImageOut)
async def scan_text_from_image(images: list[UploadFile], current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):

    file_scan_ids = []
    for image in images:
        print(f"Image Name: {image.filename}")
        print(f"Image Content Type: {image.content_type}")

        # validating the file mime type to png or jpeg
        if(image.content_type not in ["image/png", "image/jpeg"]):
            print("File format not valid.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")

        # uploading file to minIO
        await put_image_to_bucket(image_obj=image)

        # saving file result in db
        file_scan_id = await create_image_scan(current_user_email, image.filename, db)
        file_scan_ids.append(file_scan_id)

    # informing ocr_api to start scanning
    # response = await call_images_api()
    # if response is None:
    #     print("ERROR: OCR API is unavailable")
    #     raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Please contact team.")
    try:
        timeloop_app.start()
    except RuntimeError:
        print("scanning already in progress")

    response: ScanImageOut = ScanImageOut(message="Image scanning queued", scan_ids=file_scan_ids)
    return response


@router.post("/scan_videos", response_model=ScanVideoOut)
async def scan_text_from_video(videos: list[UploadFile], background_tasks: BackgroundTasks, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):

    for video in videos:
        print(f"Video Name: {video.filename}")
        print(f"Video Content Type: {video.content_type}")

        if(video.content_type not in ["video/mp4"]):
                print("Video format not valid.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video type.")

    user_id = await get_user_id_by_email(current_user_email, db)
    background_tasks.add_task(call_videos_api, videos, user_id)

    response: ScanVideoOut = ScanVideoOut(message="video scanning queued")
    return response


# get all scans of current user
@router.post("/start_scanning", response_model=StartScanningOut)
async def start_scanning():
    try:
        timeloop_app.start()
    except RuntimeError:
        print("scanning already in progress")

    response: StartScanningOut = StartScanningOut(message="done")
    return response


@router.get("/stop_scanning")
async def stop_scanning():
    timeloop_app.stop()
    return


# get all scans of current user
@router.get("/image_scans", response_model=GetImageScansOut)
async def get_image_scans(skip: int = 0, limit: int = 10, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    image_scans = await get_all_image_results(skip, limit, current_user_email, db)
    response: GetImageScansOut = GetImageScansOut(image_scans=image_scans)
    return response


# get single scan of current user with a scan id (FileResult.id)
@router.get("/image_scan", response_model=GetScanOut)
async def get_image_scan(image_scan_id: int, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    image_scan = await get_image_result(image_scan_id, current_user_email, db)
    if not image_scan:
        raise HTTPException(status_code=404, detail="Image scan not found")

    response: GetScanOut = GetScanOut(image_scan=image_scan)
    return response


@router.get("/video_scans", response_model=GetVideoScansOut)
async def get_video_scans(skip: int = 0, limit: int = 10, current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    video_scans = await get_all_videos(skip, limit, current_user_email, db)
    response: GetVideoScansOut = GetVideoScansOut(video_scans=video_scans)
    return response


@router.get("/video_scan", response_model=GetVideoScanOut)
async def get_video_scan(video_id: int, frame_skip: int = 0, frame_limit: int = 10,current_user_email: User = Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    video_scan = await get_video(video_id, frame_skip, frame_limit, current_user_email, db)
    if not video_scan:
        raise HTTPException(status_code=404, detail="Video scan not found")
    response: GetVideoScanOut = GetVideoScanOut(video_scan=video_scan)
    return response