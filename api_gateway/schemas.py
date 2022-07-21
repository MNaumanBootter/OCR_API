from pydantic import BaseModel
import datetime


class IndexOut(BaseModel):
    message: str

class SignupIn(BaseModel):
    email: str
    password: str


class SignupOut(BaseModel):
    email: str

    class Config:
        orm_mode = True


class LoginIn(BaseModel):
    email: str
    password: str


class LoginOut(BaseModel):
    token: str


class ImageResult(BaseModel):
    id: int
    file_name: str
    result: list[str]
    is_scanned: bool
    created_date: datetime.datetime

    class Config:
        orm_mode = True

class ScanImageOut(BaseModel):
    message: str
    scan_ids: list[int]


class ScanVideoOut(BaseModel):
    message: str
    video_scan_id: int

class GetImageScansOut(BaseModel):
    image_results: list[ImageResult]


class GetScanOut(BaseModel):
    image_results: ImageResult


class VideoWithoutFrames(BaseModel):
    id: int
    video_name: str
    is_scanned: bool
    frames_count: int
    created_date: datetime.datetime

    class Config:
        orm_mode = True

class GetVideoScansOut(BaseModel):
    videos: list[VideoWithoutFrames]


class VideoWithFrames(BaseModel):
    id: int
    video_name: str
    is_scanned: bool
    frames_count: int
    created_date: datetime.datetime
    frames: list[ImageResult]


    class Config:
        orm_mode = True

class GetVideoScanOut(BaseModel):
    video: VideoWithFrames