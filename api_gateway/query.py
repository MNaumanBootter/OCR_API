from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, FileResult
from minio import Minio
import http3


minio_client = Minio(
        "192.168.20.102:9000",
        secure=False,
        access_key="minioadmin",
        secret_key="minioadmin"
    )

if not minio_client.bucket_exists("ocr-api-images"):
    minio_client.make_bucket("ocr-api-images")
else:
    print("Bucket 'ocr-api-images' connected")


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


async def get_all_file_results(user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    file_results = db.query(FileResult).filter(FileResult.user_id == user_id, FileResult.is_scanned == True).all()
    return file_results


async def get_file_result(file_result_id, user_email: str, db: Session):
    user_id = await get_user_id_by_email(user_email, db)
    file_result = db.query(FileResult).filter(FileResult.id == file_result_id, FileResult.user_id == user_id).first()
    return file_result


async def put_image_to_bucket(image_obj):
    image_length = len(image_obj.file.read())
    image_obj.file.seek(0)

    minio_client.put_object(
        bucket_name="ocr-api-images",
        object_name=image_obj.filename,
        length=image_length,
        data=image_obj.file
    )
    return


async def call_endpoint(url: str):
    http_async_client = http3.AsyncClient()
    r = await http_async_client.get(url)
    return r.text