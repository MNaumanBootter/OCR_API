from typing import Union
from pydantic import BaseModel


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


class OcrFileResult(BaseModel):
    id: int
    file_name: str
    result: list[str]
    is_scanned: bool

    class Config:
        orm_mode = True


class ScanImageOut(BaseModel):
    message: str
    scan_ids: list[int]


class ScanVideoOut(BaseModel):
    message: str
    scan_ids: list[int]

class GetScansOut(BaseModel):
    results: list[OcrFileResult]


class GetScanOut(BaseModel):
    result: OcrFileResult
