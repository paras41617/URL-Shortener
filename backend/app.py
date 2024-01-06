from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
import datetime
import shortuuid

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost:5433/one'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a random secret key
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), unique=True)

class ShortLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(255), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    click_count = db.Column(db.Integer, default=0)

# Functions
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return RevokedToken.query.filter_by(jti=jti).first() is not None

def generate_short_url():
    while True:
        unique_id = shortuuid.uuid()[:8]
        existing_link = ShortLink.query.filter_by(short_url=unique_id).first()
        if not existing_link:
            return unique_id


# Routes
@app.route('/')
@jwt_required()
def home():
    current_user = get_jwt_identity()
    return jsonify({'message': f'{current_user}', 'status': 'success'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        expires = datetime.timedelta(minutes=15)
        jwt_token = create_access_token(identity=username, expires_delta=expires)
        response = jsonify({'jwt_token': jwt_token, 'status': 'success'})
        return response, 200
    return jsonify({'message': 'Invalid username or password', 'status': 'fail'}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    revoked_token = RevokedToken(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()

    response = jsonify({'message': 'Logout successful', 'status': 'success'})
    response.delete_cookie('jwt_token')
    return response, 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists', 'status': 'fail'}), 409

    try:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        response = jsonify({'message': 'Registration successful', 'status': 'success'})
        return response, 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Registration failed due to an integrity error', 'status': 'fail'}), 500

@app.route('/shorten', methods=['POST'])
@jwt_required()
def shorten_url():
    current_user = get_jwt_identity()
    data = request.get_json()
    original_url = data.get('original_url')

    user = User.query.filter_by(username=current_user).first()

    if user:
        existing_link = ShortLink.query.filter_by(original_url=original_url, user_id=user.id).first()

        if existing_link:
            short_url = existing_link.short_url
            expires_at = existing_link.expires_at
            response = jsonify({'short_url': f'http://127.0.0.1:5000/s/{short_url}', 'expires_at': expires_at.isoformat(), 'status': 'success'})
            return response, 200

        short_url = generate_short_url()
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=48)

        new_link = ShortLink(original_url=original_url, short_url=short_url, expires_at=expires_at, user_id=user.id, click_count=0)
        db.session.add(new_link)
        db.session.commit()

        response = jsonify({'short_url': f'http://127.0.0.1:5000/s/{short_url}', 'expires_at': expires_at.isoformat(), 'status': 'success'})
        return response, 201
    else:
        return jsonify({'message': 'User not found', 'status': 'fail'}), 404
        
@app.route('/s/<short_url>', methods=['GET'])
def redirect_to_original(short_url):
    link = ShortLink.query.filter_by(short_url=short_url).first()
    if link:
        if link.expires_at and link.expires_at < datetime.datetime.utcnow():
            return jsonify({'message': 'Link has expired', 'status': 'fail'}), 410 
        
        link.click_count += 1
        db.session.commit()

        return redirect(link.original_url)
    else:
        return jsonify({'message': 'Short link not found', 'status': 'fail'}), 404
    
@app.route('/analytics', methods=['GET'])
@jwt_required()
def link_analytics():
    current_user = get_jwt_identity()
    
    user = User.query.filter_by(username=current_user).first()
    
    if user:
        user_links = ShortLink.query.filter_by(user_id=user.id).all()

        analytics_data = [{'short_url': f'http://127.0.0.1:5000/s/{link.short_url}', 'original_url': link.original_url, 'click_count': link.click_count, 'created_at': link.created_at.isoformat(), 'expires_at': link.expires_at.isoformat()} for link in user_links]

        response = jsonify({'analytics': analytics_data, 'status': 'success'})
        return response, 200
    else:
        return jsonify({'message': 'User not found', 'status': 'fail'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
