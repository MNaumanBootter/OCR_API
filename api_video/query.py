from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ImageScan, VideoScan
from sqlalchemy.exc import IntegrityError
from minio import Minio
import requests
from io import BytesIO
from PIL import Image
from video_to_image import convert_video_to_images
from config import app_config
import json


minio_client = Minio(
        f"{app_config.MINIO_HOST}:{app_config.MINIO_PORT}",
        secure=False,
        access_key=app_config.MINIO_USER,
        secret_key=app_config.MINIO_PASSWORD
    )

if not minio_client.bucket_exists(app_config.MINIO_IMAGE_BUCKET):
    minio_client.make_bucket(app_config.MINIO_IMAGE_BUCKET)
else:
    print(f"Bucket {app_config.MINIO_IMAGE_BUCKET} connected")

if not minio_client.bucket_exists(app_config.MINIO_VIDEO_BUCKET):
    minio_client.make_bucket(app_config.MINIO_VIDEO_BUCKET)
else:
    print(f"Bucket {app_config.MINIO_VIDEO_BUCKET} connected")



def create_video_images(video_id: str, images_number: int, db: Session):
    video = db.query(VideoScan).filter(VideoScan.id == video_id).first()
    video_name = video.video_name
    user_id  = video.user_id
    video.frames_count = images_number

    for image_index in range(images_number):
        image_filename = f"{video_name}_{image_index}.jpg"
        created_image_result = ImageScan(user_id=user_id, file_name=image_filename, result=[])
        video.frames.append(created_image_result)

        db.add(created_image_result)

    db.commit()
    db.refresh(video)
    return video.id


def get_video_name_by_id(video_scan_id: int, db: Session):
    video = db.query(VideoScan).filter(VideoScan.id == video_scan_id).first()
    if video:
        video_name = video.video_name
    else:
        video_name = None
    return video_name


def get_video_from_bucket(video_name):
    file_bytes = minio_client.get_object(app_config.MINIO_VIDEO_BUCKET, video_name).read()
    return file_bytes


def put_video_to_bucket(video_obj):
    image_length = len(video_obj.file.read())
    video_obj.file.seek(0)

    minio_client.put_object(
        bucket_name=app_config.MINIO_VIDEO_BUCKET,
        object_name=video_obj.filename,
        length=image_length,
        data=video_obj.file
    )
    video_obj.file.seek(0)
    return


def put_video_image_to_bucket(image_ndarrray, image_filename):

    pil_image = Image.fromarray(image_ndarrray.asnumpy())
    image_bytes = BytesIO()
    pil_image.save(image_bytes, format='jpeg')
    image_length = image_bytes.tell()
    image_bytes.seek(0)

    minio_client.put_object(
        bucket_name=app_config.MINIO_IMAGE_BUCKET,
        object_name=image_filename,
        length=image_length,
        data=image_bytes
    )
    return


def create_video_scan(user_id: str, video_name: str, num_of_images: int, db: Session):
    try:
        created_video = VideoScan(user_id=user_id, video_name=video_name, frames_count=num_of_images)

        db.add(created_video)
        db.commit()
        db.refresh(created_video)
    except IntegrityError:
        return None
    return created_video.id


def process_videos(user_id: int, videos: list[UploadFile], db: Session):
    for video in videos:

        # uploading image to minIO
        put_video_to_bucket(video)

        # creating frames from video
        video_bytes = video.file.read()
        images = convert_video_to_images(video_bytes)

        # creating a video record
        video_scan_id = create_video_scan(
            user_id=user_id,
            video_name=video.filename,
            num_of_images=len(images),
            db=db
            )

        # sending 404 status if the user id was not found
        if not video_scan_id:
            raise HTTPException(status_code=404, detail="User id invalid")

        with SessionLocal() as db:
            video_created = db.query(VideoScan).filter(VideoScan.id == video_scan_id).first()

            for image_index, image in enumerate(images):
                image_filename = f"{video.filename}_{image_index}.jpg"
                created_image_result = ImageScan(user_id=user_id, file_name=image_filename, result=[])
                video_created.frames.append(created_image_result)

                # uploading image to minIO
                put_video_image_to_bucket(image_ndarrray=image, image_filename=image_filename)

                db.add(created_image_result)

                if not image_index%100:
                    print(image_index)
                if image_index == 5:
                    # call ocr image scanning api
                    send_gateway_api_scanning_request(user_id, video_created.id)

            # video_created.is_processed_to_images = True
            db.commit()

        return


def call_scanning_api():
    url = f"http://{app_config.API_OCR_URL}/start_scanning"
    r = requests.get(url)
    return r.text


def send_gateway_api_scanning_request(user_id: int, video_id: int):
    try:
        url = f"http://{app_config.API_GATEWAY_URL}/start_scanning"
        # r = requests.post(url, data=json.dumps({"user_id": user_id, "video_id": video_id}))
        r = requests.post(url)
        print(r.text)
    except requests.exceptions.ConnectionError:
        print("Error: gateway api unavailable")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="unavailable")

    return r.text