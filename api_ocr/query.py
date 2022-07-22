from sqlalchemy.orm import Session
from models import User, ImageScan
from sqlalchemy.orm import Session


async def get_user_id_by_email(email: str, db: Session):
    current_user = db.query(User).filter(User.email == email).first()
    user_id = current_user.id
    return user_id


async def create_file_result(user_id: int, file_name: str, result: list, db: Session):
    created_file_result = ImageScan(user_id=user_id, file_name=file_name, result=result)
    db.add(created_file_result)
    db.commit()
    db.refresh(created_file_result)
    return created_file_result.id


