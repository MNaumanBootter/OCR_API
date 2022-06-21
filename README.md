# OCR_API
An API that takes an image as input and responds with the English text extracted from the image by using OCR technology.

# Technology used: 
Framework: FastAPI


# Required libraries:
- pip install fastapi
- pip install easyocr
- pip install uvicorn

# Installation / Running:
From the root directory of the API where app.py is present run the following command:

    uvicorn app:app

# Endpoints:
- localhost:8000/scan_text    (for scanning text from image)
- localhost:8000/docs7        (for swagger docs)
