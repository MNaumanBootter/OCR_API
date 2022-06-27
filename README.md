# OCR_API
An API that takes an image as input and responds with the English text extracted from the image by using OCR technology.

# Technology used:
Framework: FastAPI  
Database ORM package: SQLAlchemy  
Database Migration package: Alembix  
Documentation packege: Swagger  
Containerization software: Docker  

# Installation / Running:
## Configure .env file
Write env variable values in the ".env" file with reference to the ".env-example" file. Set "ENV" variable to "development".

## Configure database
Create a database with the same database name given in the ".env" file.

## Running without Docker
Install required Python packages

    pip install -r requirements.txt

From the root directory of the API where main.py is present run the following command:

    uvicorn main:app --host 0.0.0.0 --port 8000

## Running with Docker
From the root directory of the API where Dockerfile is present run the following command:

    docker compose up --build

# Swagger Endpoint:
- localhost:8000/docs