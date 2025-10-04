from app import create_app, db
from models import User, Profile, ProfileType
from werkzeug.security import generate_password_hash
import random

def create_demo_users():
    """Create demo users and profiles"""
    
    # Demo tourist
    tourist = User(
        email="tourist@demo.com",
        password_hash=generate_password_hash("demo123"),
        points_balance=100
    )
    db.session.add(tourist)
    db.session.flush()
    
    tourist_profile = Profile(
        user_id=tourist.id,
        name="Jan Kowalski",
        age=26,
        bio="Zwiedzam Polskę i szukam lokalnych przewodników!",
        location="Warszawa",
        profile_type=ProfileType.TOURIST,
        photo_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400"
    )
    db.session.add(tourist_profile)
    
    # Demo guides
    guides_data = [
        {
            "email": "anna@demo.com",
            "name": "Anna Kowalska",
            "age": 28,
            "location": "Kraków, Stare Miasto",
            "bio": "Lokalny food expert! Znam najlepsze pierogi w mieście 🥟",
            "specialties": ["Food Tours", "Local Cuisine"],
            "hourly_rate": 25,
            "rating": 4.8
        },
        {
            "email": "michal@demo.com", 
            "name": "Michał Nowak",
            "age": 32,
            "location": "Warszawa, Śródmieście",
            "bio": "Historyk i przewodnik miejski 🏛️",
            "specialties": ["History Tours", "Architecture"],
            "hourly_rate": 30,
            "rating": 4.9
        }
    ]
    
    for guide_data in guides_data:
        user = User(
            email=guide_data["email"],
            password_hash=generate_password_hash("demo123"),
            points_balance=200
        )
        db.session.add(user)
        db.session.flush()
        
        profile = Profile(
            user_id=user.id,
            name=guide_data["name"],
            age=guide_data["age"],
            bio=guide_data["bio"],
            location=guide_data["location"],
            specialties=guide_data["specialties"],
            hourly_rate=guide_data["hourly_rate"],
            average_rating=guide_data["rating"],
            total_reviews=random.randint(20, 50),
            profile_type=ProfileType.GUIDE,
            photo_url=f"https://images.unsplash.com/photo-{random.randint(1000000, 9999999)}?w=400"
        )
        db.session.add(profile)
    
    db.session.commit()
    print("Demo users created successfully!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_demo_users()
