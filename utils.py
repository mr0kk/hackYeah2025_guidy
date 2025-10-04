from models import db, User, Profile, Match, Swipe, ProfileType, SwipeDirection
from datetime import datetime
import random

def create_match_if_mutual(user1_id, user2_id):
    """Check if both users liked each other and create match"""
    # Check if other user already liked this user
    mutual_swipe = Swipe.query.filter_by(
        swiper_id=user2_id,
        swiped_id=user1_id
    ).first()
    
    if mutual_swipe and mutual_swipe.is_like():
        # Check if match already exists
        existing_match = Match.query.filter(
            db.or_(
                db.and_(Match.user1_id == user1_id, Match.user2_id == user2_id),
                db.and_(Match.user1_id == user2_id, Match.user2_id == user1_id)
            )
        ).first()
        
        if not existing_match:
            # Create new match
            match = Match(
                user1_id=min(user1_id, user2_id),  # Consistent ordering
                user2_id=max(user1_id, user2_id)
            )
            db.session.add(match)
            return match
    
    return None

def get_nearby_profiles(user_id, radius_km=50, limit=10):
    """Get profiles near user location (mock implementation)"""
    # For hackathon - just return random profiles
    profiles = Profile.query.filter(
        Profile.user_id != user_id,
        Profile.profile_type.in_([ProfileType.GUIDE, ProfileType.BOTH])
    ).limit(limit).all()
    
    return profiles

def generate_mock_profiles(count=10):
    """Generate mock profiles for demo"""
    mock_data = [
        {
            "name": "Anna Kowalska",
            "age": 28,
            "location": "Kraków, Stare Miasto",
            "bio": "Lokalny food expert! Znam najlepsze pierogi w mieście i ukryte skarby kulinarnej Krakowa 🥟✨",
            "specialties": ["Food Tours", "Local Cuisine", "Historic Restaurants"],
            "languages": ["Polish", "English", "German"],
            "photo_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400",
            "hourly_rate": 25,
            "rating": 4.8
        },
        {
            "name": "Michał Nowak", 
            "age": 32,
            "location": "Warszawa, Śródmieście",
            "bio": "Historyk i przewodnik miejski. Pokażę Ci Warszawę, której nie znajdziesz w guidebooku! 🏛️📚",
            "specialties": ["History Tours", "Architecture", "Museums"],
            "languages": ["Polish", "English", "French"],
            "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
            "hourly_rate": 30,
            "rating": 4.9
        },
        {
            "name": "Zofia Wiśniewska",
            "age": 25, 
            "location": "Gdańsk, Stare Miasto",
            "bio": "Miłośniczka sztuki i lokalnej kultury. Oprowadzę Cię po najpiękniejszych galeriach i artystycznych dzielnicach! 🎨",
            "specialties": ["Art Tours", "Galleries", "Street Art"],
            "languages": ["Polish", "English"],
            "photo_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400",
            "hourly_rate": 22,
            "rating": 4.7
        },
        {
            "name": "Jakub Lewandowski",
            "age": 29,
            "location": "Wrocław, Market Square", 
            "bio": "Nocne życie to moja pasja! Pokażę Ci najlepsze kluby, puby i miejsca na imprezę we Wrocławiu 🌃🍻",
            "specialties": ["Nightlife", "Pubs", "Live Music"],
            "languages": ["Polish", "English"],
            "photo_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400",
            "hourly_rate": 20,
            "rating": 4.6
        },
        {
            "name": "Marta Zielińska",
            "age": 31,
            "location": "Poznań, Old Market",
            "bio": "Aktywna i pełna energii! Rowery, jogging, outdoor activities - poznaj Poznań w aktywny sposób! 🚴‍♀️🏃‍♀️",
            "specialties": ["Active Tours", "Cycling", "Outdoor Activities"],
            "languages": ["Polish", "English", "Spanish"],
            "photo_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400",
            "hourly_rate": 28,
            "rating": 4.8
        }
    ]
    
    profiles = []
    for i, data in enumerate(mock_data[:count]):
        # Create mock user first
        mock_user_id = 1000 + i  # Use high IDs to avoid conflicts
        
        profile = Profile(
            user_id=mock_user_id,
            name=data["name"],
            age=data["age"],
            location=data["location"],
            bio=data["bio"],
            photo_url=data["photo_url"],
            specialties=data["specialties"],
            languages=data["languages"],
            hourly_rate=data["hourly_rate"],
            average_rating=data["rating"],
            total_reviews=random.randint(15, 50),
            profile_type=ProfileType.GUIDE
        )
        profiles.append(profile)
    
    return profiles

def calculate_points_for_booking(guide_hourly_rate, duration_hours=2):
    """Calculate points needed for booking"""
    base_cost = guide_hourly_rate * duration_hours
    return int(base_cost * 0.8)  # 20% platform discount

def send_welcome_message(match_id):
    """Send automated welcome message for new matches"""
    welcome_messages = [
        "Cześć! Cieszę się, że się poznajemy! 😊",
        "Hej! Gotowy/a na niesamowitą przygodę po mieście?",
        "Witaj! Pokażę Ci miejsca, które kocham w tym mieście ❤️",
        "Cześć! Mam dla Ciebie kilka świetnych pomysłów na zwiedzanie!"
    ]
    
    # This would send an automated message from the guide
    # Implementation depends on business logic
    pass

def validate_image_upload(file):
    """Validate uploaded image file"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    
    if '.' not in file.filename:
        return False, "No file extension"
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"Allowed extensions: {', '.join(allowed_extensions)}"
    
    # Check file size (max 5MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset
    
    if file_size > 5 * 1024 * 1024:
        return False, "File too large (max 5MB)"
    
    return True, "Valid"

def get_user_statistics(user_id):
    """Get user statistics for profile"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Calculate statistics
    total_matches = Match.query.filter(
        db.or_(Match.user1_id == user_id, Match.user2_id == user_id)
    ).count()
    
    total_swipes_sent = Swipe.query.filter_by(swiper_id=user_id).count()
    total_likes_received = Swipe.query.filter_by(swiped_id=user_id)\
                                      .filter(Swipe.direction.in_([SwipeDirection.RIGHT, SwipeDirection.UP]))\
                                      .count()
    
    return {
        'total_matches': total_matches,
        'total_swipes_sent': total_swipes_sent,
        'total_likes_received': total_likes_received,
        'match_rate': round(total_matches / max(total_swipes_sent, 1) * 100, 1)
    }
