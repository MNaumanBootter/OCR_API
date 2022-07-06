from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from auth import auth_handler
from schemas import ScanTextFromImageSingleFile, ScanTextFromImageOut
import easyocr
import shutil


router = APIRouter()

# initializing OCR reader
ocr_reader = easyocr.Reader(['en'], gpu=False, download_enabled=False)

# this endpoint takes an image and returns the english text extracted by OCR
@router.post("/scan_text", dependencies=[Depends(auth_handler.auth_wrapper)], response_model=ScanTextFromImageOut)
async def scan_text_from_image(images: list[UploadFile]):

    result_list = []

    for image in images:
        print(f"File Name: {image.filename}")
        print(f"File Content Type: {image.content_type}")

        # validating the file mime type to png or jpeg
        if(image.content_type not in ["image/png", "image/jpeg"]):
            print("File format not valid.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")

        # path to store images
        destination_file_path = "./images/"+image.filename

        # saving images
        with open(destination_file_path, "wb") as image_buffer:
            shutil.copyfileobj(image.file, image_buffer)

        # scanning image by OCR reader
        ocr_result = ocr_reader.readtext(destination_file_path)
        ocr_result_text_list = [text for (bbox, text, prob) in ocr_result]

        result_list.append(ScanTextFromImageSingleFile(file_name=image.filename, result_text=ocr_result_text_list))

    print(f"Files scanned successfully.")

    response: ScanTextFromImageOut = ScanTextFromImageOut(result=result_list)
    return response