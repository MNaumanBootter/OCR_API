from fastapi import APIRouter
from celery_tasks import scan_image
from schemas import StartScanningOut


router = APIRouter()


# this endpoint starts ocr scanning through a celery task
@router.get("/start_scanning", response_model=StartScanningOut)
async def scan_text_from_image():
    scan_image.delay()
    response: StartScanningOut = StartScanningOut(message="Scanning started")
    return response
