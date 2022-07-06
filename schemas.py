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


class ScanTextFromImageSingleFile(BaseModel):
    file_name: str
    result_text: list[str]

class ScanTextFromImageOut(BaseModel):
    result: list[ScanTextFromImageSingleFile]