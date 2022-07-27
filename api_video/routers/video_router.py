from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile
from schemas import VideoToImagesOut
from sqlalchemy.orm import Session
from database import get_db
from video_to_image import convert_video_to_images
from query import get_video_name_by_id, get_video_from_bucket, create_video_images, put_video_image_to_bucket, process_videos, call_scanning_api


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


# this endpoint converts video to images/frames using a celery task
@router.post("/scan_videos", response_model=VideoToImagesOut)
def scan_videos(videos: list[UploadFile], user_id: int = Body(),  db: Session = Depends(get_db)):

    process_videos(user_id, videos, db)
    # for video in videos:
    #     if(video.content_type not in ["video/mp4"]):
    #         print("Video format not valid.")
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video type.")


        # video_scan_id = create_video_scan(
        #     user_id=user_id,
        #     video_name=video.filename,
        #     db=db
        #     )

        # if not video_scan_id:
        #     raise HTTPException(status_code=404, detail="User id invalid")

        # images = convert_video_to_images(video.file.read())

        # create_video_images(
        #     video_id=video_scan_id,
        #     images_number=len(images),
        #     db=db
        #     )

        # for image_index, image in enumerate(images):
        #     image_filename = f"{video.filename}_{image_index}.jpg"
        #     # uploading file to minIO
        #     put_video_image_to_bucket(image_ndarrray=image, image_filename=image_filename)

        # informing ocr_api to start scanning
        # call_scanning_api()

    response: VideoToImagesOut = VideoToImagesOut(message="Video frames added database and uploaded to MinIO")
    return response