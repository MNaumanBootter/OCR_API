from anyio import start_blocking_portal
from fastapi import APIRouter, Depends, HTTPException
# from celery_tasks import scan_image
from schemas import VideoToImagesOut
from sqlalchemy.orm import Session
from database import get_db
from video_to_image import convert_video_to_images
from query import get_video_name_by_id, get_video_from_bucket, create_video_images, put_video_image_to_bucket, call_scanning_api


router = APIRouter()


# this endpoint converts video to images/frames using a celery task
@router.get("/video_to_images", response_model=VideoToImagesOut)
def video_to_images(video_scan_id: int, db: Session = Depends(get_db)):

    video_name = get_video_name_by_id(video_scan_id, db)
    if not video_name:
        raise HTTPException(status_code=404, detail="Video scan not found")

    video = get_video_from_bucket(video_name)
    images = convert_video_to_images(video)

    create_video_images(
        video_id=video_scan_id,
        images_number=len(images),
        db=db
        )

    for image_index, image in enumerate(images):
        image_filename = f"{video_name}_{image_index}.jpg"
        # uploading file to minIO
        put_video_image_to_bucket(image_ndarrray=image, image_filename=image_filename)

    # informing ocr_api to start scanning
    call_scanning_api()

    response: VideoToImagesOut = VideoToImagesOut(message="Video frames added database and uploaded to MinIO")
    return response