from pydantic import BaseModel


class IndexOut(BaseModel):
    message: str


class StartScanningOut(BaseModel):
    message: str