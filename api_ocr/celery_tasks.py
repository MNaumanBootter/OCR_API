from config import app_config
from minio import Minio
from celery import Celery
from sqlalchemy.orm import Session
from models import ImageResult
from database import SessionLocal
import easyocr
from config import app_config


# initializing celery
celery = Celery()
celery.conf.broker_url = app_config.CELERY_BROKER_URL
celery.conf.result_backend = app_config.CELERY_RESULT_URL


# initializing MinIO
minio_client = Minio(
        f"{app_config.MINIO_HOST}:{app_config.MINIO_PORT}",
        secure=False,
        access_key=app_config.MINIO_USER,
        secret_key=app_config.MINIO_PASSWORD
    )


# initializing OCR reader
ocr_reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=r"ocr_models")


# defining a celery task for scanning image with ocr reader
@celery.task(name='scan_image')
def scan_image():
    db: Session = SessionLocal()
    try:
        # loop until all records are scanned
        while(True):
            # getting unscanned record
            unscanned_record: ImageResult = db.query(ImageResult).filter(ImageResult.is_scanned == False).first()

            # if unscanned record found
            if unscanned_record:

                # fetching file bytes from minIO
                file_bytes = minio_client.get_object(app_config.MINIO_BUCKET, unscanned_record.file_name).read()

                # predicting image from ocr reader without bbox result
                ocr_result = ocr_reader.readtext(file_bytes, detail=0)

                # updating record
                unscanned_record.result = ocr_result
                unscanned_record.is_scanned = True
                db.commit()

            # if no unscanned record found then break loop
            else:
                break

    finally:
        db.close()

    return {"status": 'scanned successfully'}