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
    text_lines: list[str]

class ScanTextFromImageOut(BaseModel):
    result: list[OcrFileResult]