from sqlalchemy.orm import Session
from models import User, ImageResult, Video
from minio import Minio
import http3
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


async def get_user_id_by_email(email: str, db: Session):
    current_user = db.query(User).filter(User.email == email).first()
    user_id = current_user.id
    return user_id


async def create_image_result(user_email: str, file_name: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    created_image_result = ImageResult(user_id=user_id, file_name=file_name, result=[])
    db.add(created_image_result)
    db.commit()
    db.refresh(created_image_result)
    return created_image_result.id


# async def create_video_images(user_email: str, images_number: int, video_name: str, db: Session):
#     user_id = await get_user_id_by_email(user_email, db)
#     created_video = Video(user_id=user_id, video_name=video_name, frames_count=images_number)

#     for image_index in range(images_number):
#         image_filename = f"{video_name}_{image_index}.jpg"
#         created_image_result = ImageResult(user_id=user_id, file_name=image_filename, result=[])
#         created_video.frames.append(created_image_result)

#         db.add(created_image_result)

#     db.add(created_video)
#     db.commit()
#     db.refresh(created_video)
#     return created_video.id


async def create_video_images(video_id: str, images_number: int, db: Session):
    video = db.query(Video).filter(Video.id == video_id).first()
    video_name = video.video_name
    user_id  = video.user_id

    for image_index in range(images_number):
        image_filename = f"{video_name}_{image_index}.jpg"
        created_image_result = ImageResult(user_id=user_id, file_name=image_filename, result=[])
        video.frames.append(created_image_result)

        db.add(created_image_result)

    db.commit()
    db.refresh(video)
    return video.id


async def create_video(user_email: str, video_name: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    created_video = Video(user_id=user_id, video_name=video_name)

    db.add(created_video)
    db.commit()
    db.refresh(created_video)
    return created_video.id


async def get_video_name_by_id(video_id: int, db: Session):
    video = db.query(Video).filter(Video.id == video_id).first()
    video_name = video.video_name
    return video_name


async def get_video_from_bucket(video_name):
    file_bytes = minio_client.get_object(app_config.MINIO_VIDEO_BUCKET, video_name).read()
    return file_bytes


async def get_all_image_results(skip: int, limit: int, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    image_results = db.query(ImageResult).filter(ImageResult.user_id == user_id, ImageResult.video_id.is_(None)).offset(skip).limit(limit).all()
    return image_results


async def get_image_result(file_result_id, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    image_result = db.query(ImageResult).filter(ImageResult.id == file_result_id, ImageResult.user_id == user_id).first()
    return image_result


async def get_all_videos(skip: int, limit: int, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    videos = db.query(Video).filter(Video.user_id == user_id).offset(skip).limit(limit).all()
    return videos


async def get_video(video_id: int, frame_skip, frame_limit, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    video = db.query(Video).filter(Video.id == video_id, ImageResult.user_id == user_id).first()
    video.frames = video.frames[frame_skip : frame_skip+frame_limit]
    return video


async def put_image_to_bucket(image_obj):
    image_length = len(image_obj.file.read())
    image_obj.file.seek(0)

    minio_client.put_object(
        bucket_name=app_config.MINIO_IMAGE_BUCKET,
        object_name=image_obj.filename,
        length=image_length,
        data=image_obj.file
    )
    return

async def put_video_image_to_bucket(image_ndarrray, image_filename):

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


async def put_video_to_bucket(video_obj):
    image_length = len(video_obj.file.read())
    video_obj.file.seek(0)

    minio_client.put_object(
        bucket_name=app_config.MINIO_VIDEO_BUCKET,
        object_name=video_obj.filename,
        length=image_length,
        data=video_obj.file
    )
    return


async def call_endpoint(url: str):
    http_async_client = http3.AsyncClient()
    r = await http_async_client.get(url)
    return r.text