from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
# from flask import Flask

Base = declarative_base()

db = SQLAlchemy()
"""
Simple table structures that stores all tokenHourlyData in one table and references the token table where we're storing the latest token metadata
"""
class TokenHourData(Base):
    __tablename__ = 'token_hourly_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    close = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    open = db.Column(db.Float)
    price_usd = db.Column(db.Float)
    token_address = db.Column(db.String(50), db.ForeignKey('token.address'))
    
    token = db.relationship('Token', backref='data')
    
class Token(Base):
    __tablename__ = 'token'
    
    address = db.Column(db.String(50), primary_key=True)
    decimals = db.Column(db.Integer)
    symbol = db.Column(db.String(50))
    name = db.Column(db.String(100))
    volume_usd = db.Column(db.Float)
    total_supply = db.Column(db.Float)


"""
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://preeyammehta@localhost/TokenData'
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
    db.session().commit()
    print('tables created')
"""