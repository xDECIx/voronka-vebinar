from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Конфигурация базы данных
DATABASE_URL = 'sqlite:///users.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Определение модели пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='alive')
    status_updated_at = Column(DateTime, default=datetime.datetime.utcnow)

# Инициализация базы данных
def init_db():
    Base.metadata.create_all(engine)
