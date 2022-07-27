from sqlalchemy.orm import Session
from models import User, ImageScan, VideoScan
from minio import Minio
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


async def create_image_scan(user_email: str, file_name: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    created_image_result = ImageScan(user_id=user_id, file_name=file_name, result=[])
    db.add(created_image_result)
    db.commit()
    db.refresh(created_image_result)
    return created_image_result.id


async def create_video_scan(user_email: str, video_name: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    created_video = VideoScan(user_id=user_id, video_name=video_name)

    db.add(created_video)
    db.commit()
    db.refresh(created_video)
    return created_video.id


async def get_all_image_results(skip: int, limit: int, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    image_results = db.query(ImageScan).filter(ImageScan.user_id == user_id, ImageScan.video_id.is_(None)).offset(skip).limit(limit).all()
    return image_results


async def get_image_result(file_result_id, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    image_result = db.query(ImageScan).filter(ImageScan.id == file_result_id, ImageScan.user_id == user_id).first()
    return image_result


async def get_all_videos(skip: int, limit: int, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    video_scans = db.query(VideoScan).filter(VideoScan.user_id == user_id).offset(skip).limit(limit).all()
    return video_scans


async def get_video(video_id: int, frame_skip, frame_limit, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    video_scan = db.query(VideoScan).filter(VideoScan.id == video_id, VideoScan.user_id == user_id).first()
    if video_scan:
        video_scan.frames = video_scan.frames[frame_skip : frame_skip+frame_limit]
    return video_scan


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


# async def put_video_to_bucket(video_obj):
#     image_length = len(video_obj.file.read())
#     video_obj.file.seek(0)

#     minio_client.put_object(
#         bucket_name=app_config.MINIO_VIDEO_BUCKET,
#         object_name=video_obj.filename,
#         length=image_length,
#         data=video_obj.file
#     )
#     return


# async def call_video_to_images_api(video_scan_id: int):
#     async with aiohttp.ClientSession() as session:
#         url = f"http://{app_config.API_Video_To_Images_URL}/start_scanning"
#         async with session.get(url) as response_http:
#             response = await response_http.json()
#     return response


# async def call_images_api():
#     try:
#         async with aiohttp.ClientSession() as session:
#             url = f"http://{app_config.API_OCR_URL}/start_scanning"
#             async with session.get(url) as response_http:
#                 response = await response_http.json()
#     except:
#         return None
#     return response

