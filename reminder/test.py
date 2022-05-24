from flask import jsonify
from models import User, Title, Saved
from reminder import db


title = db.session.query(Title).filter_by(tmdb_id=74220).first()
print(title.tmdb_id)
