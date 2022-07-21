from sqlalchemy import ForeignKey, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import relationship
import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    address = Column(String(255))
    is_active = Column(Boolean, default=True)


class ImageResult(Base):
    __tablename__ = "image_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    file_name = Column(String(255), nullable=False)
    is_scanned = Column(Boolean, nullable=False, default=False)
    _result = Column('result', Text())
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


    @property
    def result(self):
        return eval(self._result)
    @result.setter
    def result(self, value):
        self._result = str(value)


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_name = Column(String(255), nullable=False)
    frames_count = Column(Integer)
    is_scanned = Column(Boolean, nullable=False, default=False)
    frames = relationship("ImageResult", uselist=True, backref='videos')
    created_date = Column(DateTime, default=datetime.datetime.utcnow)