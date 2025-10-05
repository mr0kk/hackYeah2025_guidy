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
    
    # Demo guides - DODANO PHOTO_URL DO KAŻDEGO
    guides_data = [
        {
            "email": "anna@demo.com",
            "name": "Anna Kowalska",
            "age": 28,
            "location": "Kraków, Stare Miasto",
            "bio": "Lokalny food expert! Znam najlepsze pierogi w mieście 🥟",
            "specialties": ["Food Tours", "Local Cuisine"],
            "hourly_rate": 25,
            "rating": 4.8,
            "photo_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400&h=400&fit=crop&crop=face"
        },
        {
            "email": "michal@demo.com", 
            "name": "Michał Nowak",
            "age": 32,
            "location": "Warszawa, Śródmieście",
            "bio": "Historyk i przewodnik miejski 🏛️",
            "specialties": ["History Tours", "Architecture"],
            "hourly_rate": 30,
            "rating": 4.9,
            "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face"
        },
        {
            "email": "zofia@demo.com",
            "name": "Zofia Wiśniewska",
            "age": 25,
            "location": "Gdańsk, Stare Miasto",
            "bio": "Miłośniczka sztuki i lokalnej kultury. Oprowadzę Cię po najpiękniejszych galeriach! 🎨",
            "specialties": ["Art Tours", "Galleries", "Street Art"],
            "hourly_rate": 22,
            "rating": 4.7,
            "photo_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face"
        },
        {
            "email": "jakub@demo.com",
            "name": "Jakub Lewandowski", 
            "age": 29,
            "location": "Wrocław, Rynek",
            "bio": "Nocne życie to moja pasja! Pokażę Ci najlepsze kluby i puby we Wrocławiu 🌃🍻",
            "specialties": ["Nightlife", "Pubs", "Live Music"],
            "hourly_rate": 20,
            "rating": 4.6,
            "photo_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face"
        },
        {
            "email": "marta@demo.com",
            "name": "Marta Zielińska",
            "age": 31,
            "location": "Poznań, Stary Rynek",
            "bio": "Aktywna i pełna energii! Rowery, jogging, outdoor - poznaj Poznań aktywnie! 🚴‍♀️",
            "specialties": ["Active Tours", "Cycling", "Outdoor Activities"],
            "hourly_rate": 28,
            "rating": 4.8,
            "photo_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face"
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
            photo_url=guide_data["photo_url"]  # DODANO TĘ LINIĘ
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
