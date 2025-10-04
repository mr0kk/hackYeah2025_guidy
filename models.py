from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

# === USER MODEL ===
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Profile relationship
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Points
    points_balance = db.Column(db.Integer, default=50)
    total_points_earned = db.Column(db.Integer, default=0)
    total_points_spent = db.Column(db.Integer, default=0)
    
    # Relationships
    sent_swipes = db.relationship('Swipe', foreign_keys='Swipe.swiper_id', backref='swiper')
    received_swipes = db.relationship('Swipe', foreign_keys='Swipe.swiped_id', backref='swiped')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_points(self, amount, reason=""):
        self.points_balance += amount
        if amount > 0:
            self.total_points_earned += amount
        else:
            self.total_points_spent += abs(amount)
        
        # Create transaction record
        transaction = PointTransaction(
            user_id=self.id,
            amount=amount,
            reason=reason
        )
        db.session.add(transaction)
    
    def can_afford(self, amount):
        return self.points_balance >= amount
    
    def get_level(self):
        """Calculate user level based on total points earned"""
        if self.total_points_earned < 50:
            return {"level": 1, "name": "Nowicjusz"}
        elif self.total_points_earned < 150:
            return {"level": 2, "name": "Przewodnik"}
        elif self.total_points_earned < 500:
            return {"level": 3, "name": "Expert"}
        else:
            return {"level": 4, "name": "Legenda"}

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'points_balance': self.points_balance,
            'level': self.get_level(),
            'created_at': self.created_at.isoformat(),
            'profile': self.profile.to_dict() if self.profile else None
        }

# === PROFILE MODEL ===
class ProfileType(enum.Enum):
    TOURIST = "tourist"
    GUIDE = "guide"
    BOTH = "both"

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic info
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    bio = db.Column(db.Text)
    location = db.Column(db.String(200))
    
    # Photos
    photo_url = db.Column(db.String(500))
    photos = db.Column(db.JSON)  # Array of photo URLs
    
    # Guide specific
    profile_type = db.Column(db.Enum(ProfileType), default=ProfileType.TOURIST)
    hourly_rate = db.Column(db.Integer, default=25)  # in points
    specialties = db.Column(db.JSON)  # Array of specialties
    languages = db.Column(db.JSON)  # Array of languages
    availability = db.Column(db.JSON)  # Availability schedule
    
    # Ratings
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    def update_rating(self, new_rating):
        """Update average rating with new review"""
        total_score = self.average_rating * self.total_reviews
        self.total_reviews += 1
        self.average_rating = (total_score + new_rating) / self.total_reviews
        
    def is_guide(self):
        return self.profile_type in [ProfileType.GUIDE, ProfileType.BOTH]
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'bio': self.bio,
            'location': self.location,
            'photo_url': self.photo_url,
            'photos': self.photos or [],
            'profile_type': self.profile_type.value,
            'hourly_rate': self.hourly_rate,
            'specialties': self.specialties or [],
            'languages': self.languages or [],
            'average_rating': round(self.average_rating, 1),
            'total_reviews': self.total_reviews,
            'total_bookings': self.total_bookings,
            'is_guide': self.is_guide()
        }

# === SWIPE MODEL ===
class SwipeDirection(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"

class Swipe(db.Model):
    __tablename__ = 'swipes'
    
    id = db.Column(db.Integer, primary_key=True)
    swiper_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    swiped_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    direction = db.Column(db.Enum(SwipeDirection), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent double swiping
    __table_args__ = (db.UniqueConstraint('swiper_id', 'swiped_id'),)
    
    def is_like(self):
        return self.direction in [SwipeDirection.RIGHT, SwipeDirection.UP]

# === MATCH MODEL ===
class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Messages relationship
    messages = db.relationship('Message', backref='match', cascade='all, delete-orphan')
    
    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    
    def get_other_user(self, user_id):
        """Get the other user in this match"""
        return self.user2 if self.user1_id == user_id else self.user1
    
    def to_dict(self, current_user_id):
        other_user = self.get_other_user(current_user_id)
        return {
            'id': self.id,
            'other_user': other_user.to_dict(),
            'created_at': self.created_at.isoformat(),
            'last_message': self.messages[-1].to_dict() if self.messages else None
        }

# === MESSAGE MODEL ===
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    # Relationship
    sender = db.relationship('User', backref='sent_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.profile.name if self.sender.profile else 'Unknown',
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read
        }

# === POINT TRANSACTION MODEL ===
class PointTransaction(db.Model):
    __tablename__ = 'point_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive = earned, Negative = spent
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'reason': self.reason,
            'created_at': self.created_at.isoformat(),
            'type': 'earned' if self.amount > 0 else 'spent'
        }

# === BOOKING MODEL (for future) ===
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points_cost = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, completed, cancelled
    scheduled_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tourist = db.relationship('User', foreign_keys=[tourist_id])
    guide = db.relationship('User', foreign_keys=[guide_id])
