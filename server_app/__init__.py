from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = 'IYRV%$DWvbignyhuiojNJGUBFKHJhjkFVHkbj*&tuy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:altff12345@localhost/clinic_db?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['PAGE_SIZE']= 111111115

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(
    cloud_name = 'djga3njzi',
    api_key = '595946198281489',
    api_secret = 'hd1cRj177f0HVAQ-vSeqG_yT9Y0'
)





# Download the helper library from https://www.twilio.com/docs/python/install


