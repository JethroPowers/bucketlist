from app import db
from sqlalchemy import and_
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
import flask




class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    bucketlists = db.relationship(
        'Bucketlist', order_by='Bucketlist.id', cascade="all, delete-orphan")


    def __init__(self, email, password):
        """Initialize the user with an email and a password."""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""
        from run import app
        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=5),
                'iat': datetime.utcnow(),
                'sub': str(user_id)
            }
            print(payload)

            print(app.config['SECRET'])
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                flask.current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            print(jwt_string)
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            print(str(e))
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, flask.current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"

class Bucketlist(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    completion_status = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, status, created_by):
        """initialize with name."""
        self.name = name
        self.completion_status = status
        self.created_by = created_by

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_name(self):
        return self.name

    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist: {}>".format(self.name)

    @staticmethod
    def is_name_exists(bucketlist_name, user_id):
        num_rows = Bucketlist.query.filter(and_(Bucketlist.name == bucketlist_name, Bucketlist.created_by == user_id)).count()
        return num_rows > 0

    @staticmethod
    def is_name_exists_except_id(bucketlist_name, id, user_id):
        num_rows = Bucketlist.query.filter(and_(Bucketlist.name == bucketlist_name, Bucketlist.id != id,
                                                Bucketlist.created_by == user_id)).count()
        return num_rows > 0

    @staticmethod
    def status_change_only(bucketlist_name, id):
        num_rows = Bucketlist.query.filter(and_(Bucketlist.name == bucketlist_name, Bucketlist.id != id)).count()
        return num_rows > 0

class BucketlistItem(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'bucketlist_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    completion_status = db.Column(db.Boolean, default=False, nullable=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(Bucketlist.id))

    def __init__(self, name, status, bucketlist_id):
        """initialize with name."""
        self.name = name
        self.completion_status = status
        self.bucketlist_id = bucketlist_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_name(self):
        return self.name

    @staticmethod
    def get_all():
        return BucketlistItem.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def is_name_exists(item_name, bucketlist_id):
        num_rows = BucketlistItem.query.filter(and_(BucketlistItem.name == item_name,
                                               BucketlistItem.bucketlist_id == bucketlist_id)).count()
        return num_rows > 0

    @staticmethod
    def is_name_exists_except_id(bucketlist_item_name, id, bucketlist_id):
        num_rows = BucketlistItem.query.filter(and_(BucketlistItem.name == bucketlist_item_name, BucketlistItem.id != id,
                                                BucketlistItem.bucketlist_id == bucketlist_id)).count()

        return num_rows > 0
