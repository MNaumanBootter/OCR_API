from sqlalchemy import ForeignKey, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql.schema import Column
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


class FileResult(Base):
    __tablename__ = "file_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    _result = Column('result', Text(), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def result(self):
        return eval(self._result)
    @result.setter
    def result(self, value):
        self._result = str(value)