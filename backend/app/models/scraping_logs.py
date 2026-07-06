from sqlalchemy import Column, Integer, String, DateTime
from app.database.database import Base
from datetime import datetime

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"

    scraplogs_id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=False)
    duration = Column(String(30), nullable=False)
    new_records = Column(Integer, default=0)

    updated_records = Column(Integer, default=0)

    expired_records = Column(Integer, default=0)

    status = Column(String(30), nullable=False)

    error_message = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)