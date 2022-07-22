from sqlalchemy.orm import Session
from models import ImageScan, VideoScan
from minio import Minio
import requests
from io import BytesIO
from PIL import Image
from config import app_config


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


def call_scanning_api():
    url = f"http://{app_config.API_OCR_URL}/start_scanning"
    r = requests.get(url)
    return r.text