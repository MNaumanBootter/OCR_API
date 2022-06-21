from fastapi import FastAPI, File, UploadFile, HTTPException, status
import shutil
import easyocr

# declaring FastAPI app
app = FastAPI()

# index end point for checking if it is working
@app.get("/")
def index():
    return {"message": "It is working."}

# this endpoint takes an image and returns english text extracted by OCR
@app.post("/scan_text")
async def scan_text_from_image(image: UploadFile = File(...)):
    
    print(f"File Name: {image.filename}")
    print(f"File Content Type: {image.content_type}")
    
    # checking if the file content is image
    if(image.content_type not in ["image/png", "image/jpeg"]):
        print("File format not accessable.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type.")
    
    # pathing to store images
    destination_file_path = "./images/"+image.filename
    
    # saving images
    with open(destination_file_path, "wb") as image_buffer:
        shutil.copyfileobj(image.file, image_buffer)
    
    # scanning image by OCR package
    ocr_reader = easyocr.Reader(['en'], gpu=False)
    ocr_result = ocr_reader.readtext(destination_file_path)
    ocr_result_text = [text for (bbox, text, prob) in ocr_result]
    
    print(f"File scanned successfully.")
    
    return {"filename": image.filename, "result": ocr_result_text}
