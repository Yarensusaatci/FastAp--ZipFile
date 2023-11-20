from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

Base = declarative_base()

class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True)
    started_at = Column(DateTime)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String)
    progress = Column(Float)
    file_path = Column(String, nullable=True)
    
# In SQLite db, you can see these areas.
# file_path is the {downloaded image name}.zip which is in VScode
# if you want to use Vscode for open the zip, you should use "unzip {file_path}" comment in terminal


