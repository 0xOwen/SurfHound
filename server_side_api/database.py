from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

db = SQLAlchemy()

class URLStat(db.Model):
    __tablename__ = 'url_stats'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_phishing = Column(Integer)
    ip_address = Column(String)