from database import SessionLocal
from models import ImageScan
from config import app_config
from minio import Minio
import easyocr


# initializing MinIO
minio_client = Minio(
        f"{app_config.MINIO_HOST}:{app_config.MINIO_PORT}",
        secure=False,
        access_key=app_config.MINIO_USER,
        secret_key=app_config.MINIO_PASSWORD
    )

# initializing OCR reader
ocr_reader = easyocr.Reader(['en'], gpu=False, model_storage_directory=r"ocr_models")


# async def scan_image_batch(video_id: int, user_id: int):
async def scan_image_batch():

    with SessionLocal() as db:
        # unscanned_records = db.query(ImageScan).filter(ImageScan.is_scanned == False, ImageScan.user_id == user_id, ImageScan.video_id == video_id).first()
        unscanned_records = db.query(ImageScan).filter(ImageScan.is_scanned == False).limit(10).all()
        print(unscanned_records[0].id)
        if not unscanned_records:
            print("no unscanned record found")
            return False

        for unscanned_record in unscanned_records:
            # fetching file bytes from minIO
            file_bytes = minio_client.get_object(app_config.MINIO_IMAGE_BUCKET, unscanned_record.file_name).read()

            # predicting image from ocr reader without bbox result
            ocr_result = ocr_reader.readtext(file_bytes, detail=0)

            # updating record
            unscanned_record.result = ocr_result
            unscanned_record.is_scanned = True
            db.commit()

    return True


