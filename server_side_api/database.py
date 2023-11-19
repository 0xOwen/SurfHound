from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    _password = Column(String, name='password')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    urls = relationship('URLStat', backref='user')

class Admin(db.Model):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    _password = Column(String, name='password')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

class URLStat(db.Model):
    __tablename__ = 'url_stats'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_phishing = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))