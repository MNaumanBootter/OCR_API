from pydantic import BaseModel


class IndexOut(BaseModel):
    message: str


class VideoToImagesOut(BaseModel):
    message: str