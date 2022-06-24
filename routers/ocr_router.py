
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from auth import auth_handler
from schemas import ScanTextFromImageOut
import easyocr
import shutil

router = APIRouter()


# this endpoint takes an image and returns the english text extracted by OCR
@router.post("/scan_text", dependencies=[Depends(auth_handler.auth_wrapper)], response_model=ScanTextFromImageOut)
async def scan_text_from_image(image: UploadFile = File(...)):

    print(f"File Name: {image.filename}")
    print(f"File Content Type: {image.content_type}")

    # checking if the file content is image
    if(image.content_type not in ["image/png", "image/jpeg"]):
        print("File format not accessable.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")

    # path to store images
    destination_file_path = "./images/"+image.filename

    # saving images
    with open(destination_file_path, "wb") as image_buffer:
        shutil.copyfileobj(image.file, image_buffer)

    # scanning image by OCR package
    ocr_reader = easyocr.Reader(['en'], gpu=False)
    ocr_result = ocr_reader.readtext(destination_file_path)
    ocr_result_text_list = [text for (bbox, text, prob) in ocr_result]

    print(f"File scanned successfully.")

    response: ScanTextFromImageOut = {"result": ocr_result_text_list}
    return response