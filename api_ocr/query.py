from config import app_config
from minio import Minio
from sqlalchemy.orm import Session
from models import User, ImageScan

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


async def create_image_scan(user_id: int, file_name: str, db: Session):
    created_image_result = ImageScan(user_id=user_id, file_name=file_name, result=[])
    db.add(created_image_result)
    db.commit()
    db.refresh(created_image_result)
    return created_image_result.id