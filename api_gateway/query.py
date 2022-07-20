from sqlalchemy.orm import Session
from models import User, FileResult
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

if not minio_client.bucket_exists(app_config.MINIO_BUCKET):
    minio_client.make_bucket(app_config.MINIO_BUCKET)
else:
    print(f"Bucket {app_config.MINIO_BUCKET} connected")


async def get_user_id_by_email(email: str, db: Session):
    current_user = db.query(User).filter(User.email == email).first()
    user_id = current_user.id
    return user_id


async def create_file_result(user_email: str, file_name: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    created_file_result = FileResult(user_id=user_id, file_name=file_name, result=[])
    db.add(created_file_result)
    db.commit()
    db.refresh(created_file_result)
    return created_file_result.id


async def get_all_file_results(skip: int, limit: int, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    file_results = db.query(FileResult).filter(FileResult.user_id == user_id, FileResult.is_scanned == True).offset(skip).limit(limit).all()
    return file_results


async def get_file_result(file_result_id, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    file_result = db.query(FileResult).filter(FileResult.id == file_result_id, FileResult.user_id == user_id).first()
    return file_result


async def put_image_to_bucket(image_obj):
    image_length = len(image_obj.file.read())
    image_obj.file.seek(0)

    minio_client.put_object(
        bucket_name=app_config.MINIO_BUCKET,
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
        bucket_name=app_config.MINIO_BUCKET,
        object_name=image_filename,
        length=image_length,
        data=image_bytes
    )
    return


async def call_endpoint(url: str):
    http_async_client = http3.AsyncClient()
    r = await http_async_client.get(url)
    return r.text