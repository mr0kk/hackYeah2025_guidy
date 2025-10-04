from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Profile, Swipe, Match, Message, PointTransaction, SwipeDirection
from utils import get_nearby_profiles, create_match_if_mutual, generate_mock_profiles
import random

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# === AUTHENTICATION ROUTES ===
@api.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = User(
            email=data['email'],
            points_balance=50  # Starting points
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create initial points transaction
        transaction = PointTransaction(
            user_id=user.id,
            amount=50,
            reason="Welcome bonus"
        )
        db.session.add(transaction)
        db.session.commit()
        
        login_user(user)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and user.check_password(data.get('password')):
            login_user(user, remember=True)
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@api.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({'user': current_user.to_dict()}), 200

# === PROFILE ROUTES ===
@api.route('/profile', methods=['GET', 'POST'])
@login_required
def handle_profile():
    if request.method == 'GET':
        if current_user.profile:
            return jsonify({'profile': current_user.profile.to_dict()}), 200
        else:
            return jsonify({'profile': None}), 200
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            if current_user.profile:
                # Update existing profile
                profile = current_user.profile
            else:
                # Create new profile
                profile = Profile(user_id=current_user.id)
            
            # Update fields
            profile.name = data.get('name', profile.name)
            profile.age = data.get('age', profile.age)
            profile.bio = data.get('bio', profile.bio)
            profile.location = data.get('location', profile.location)
            profile.photo_url = data.get('photo_url', profile.photo_url)
            profile.specialties = data.get('specialties', profile.specialties)
            profile.languages = data.get('languages', profile.languages)
            profile.hourly_rate = data.get('hourly_rate', profile.hourly_rate)
            
            if not current_user.profile:
                db.session.add(profile)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'profile': profile.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# === SWIPE/DISCOVERY ROUTES ===
@api.route('/profiles', methods=['GET'])
@login_required
def get_profiles():
    try:
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        exclude_swiped = request.args.get('exclude_swiped', 'true').lower() == 'true'
        
        # Get already swiped profile IDs
        swiped_ids = []
        if exclude_swiped:
            swiped_profiles = db.session.query(Swipe.swiped_id).filter_by(
                swiper_id=current_user.id
            ).all()
            swiped_ids = [s[0] for s in swiped_profiles]
        
        # Query for profiles
        query = db.session.query(Profile).join(User).filter(
            User.id != current_user.id,  # Exclude self
            User.is_active == True,
            Profile.profile_type.in_(['guide', 'both'])  # Only guides
        )
        
        if swiped_ids:
            query = query.filter(~Profile.user_id.in_(swiped_ids))
        
        profiles = query.limit(limit).all()
        
        # If no real profiles, generate mock data for demo
        if not profiles:
            profiles = generate_mock_profiles(limit)
        
        return jsonify({
            'profiles': [p.to_dict() for p in profiles],
            'count': len(profiles)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/swipe', methods=['POST'])
@login_required
def swipe_profile():
    try:
        data = request.get_json()
        profile_id = data.get('profile_id')
        direction = data.get('direction')
        
        if not profile_id or not direction:
            return jsonify({'error': 'Missing profile_id or direction'}), 400
        
        # Check if already swiped
        existing_swipe = Swipe.query.filter_by(
            swiper_id=current_user.id,
            swiped_id=profile_id
        ).first()
        
        if existing_swipe:
            return jsonify({'error': 'Already swiped on this profile'}), 400
        
        # Create swipe record
        swipe = Swipe(
            swiper_id=current_user.id,
            swiped_id=profile_id,
            direction=SwipeDirection(direction)
        )
        db.session.add(swipe)
        
        # Check for match if it's a like
        match_data = None
        if swipe.is_like():
            match = create_match_if_mutual(current_user.id, profile_id)
            if match:
                # Get matched user's profile
                matched_user = User.query.get(profile_id)
                match_data = {
                    'match_id': match.id,
                    'guide_name': matched_user.profile.name if matched_user.profile else 'Unknown',
                    'guide_photo': matched_user.profile.photo_url if matched_user.profile else None,
                    'user_photo': current_user.profile.photo_url if current_user.profile else None
                }
        
        db.session.commit()
        
        response_data = {
            'message': 'Swipe recorded successfully',
            'match': match_data is not None
        }
        
        if match_data:
            response_data['match_data'] = match_data
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# === MATCH ROUTES ===
@api.route('/matches', methods=['GET'])
@login_required
def get_matches():
    try:
        matches = Match.query.filter(
            db.or_(Match.user1_id == current_user.id, Match.user2_id == current_user.id),
            Match.is_active == True
        ).order_by(Match.created_at.desc()).all()
        
        return jsonify({
            'matches': [m.to_dict(current_user.id) for m in matches],
            'count': len(matches)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === CHAT ROUTES ===
@api.route('/matches/<int:match_id>/messages', methods=['GET', 'POST'])
@login_required
def handle_messages(match_id):
    # Verify user is part of this match
    match = Match.query.get_or_404(match_id)
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        messages = Message.query.filter_by(match_id=match_id)\
                                .order_by(Message.created_at.asc()).all()
        
        # Mark messages as read
        unread_messages = [m for m in messages if not m.is_read and m.sender_id != current_user.id]
        for msg in unread_messages:
            msg.is_read = True
        db.session.commit()
        
        return jsonify({
            'messages': [m.to_dict() for m in messages]
        }), 200
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            content = data.get('content', '').strip()
            
            if not content:
                return jsonify({'error': 'Message content is required'}), 400
            
            message = Message(
                match_id=match_id,
                sender_id=current_user.id,
                content=content
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                'message': message.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# === POINTS ROUTES ===
@api.route('/user/points', methods=['GET'])
@login_required
def get_user_points():
    try:
        transactions = PointTransaction.query.filter_by(user_id=current_user.id)\
                                           .order_by(PointTransaction.created_at.desc())\
                                           .limit(20).all()
        
        return jsonify({
            'balance': current_user.points_balance,
            'total_earned': current_user.total_points_earned,
            'total_spent': current_user.total_points_spent,
            'level': current_user.get_level(),
            'recent_transactions': [t.to_dict() for t in transactions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === DEMO/UTILITY ROUTES ===
@api.route('/demo/reset', methods=['POST'])
def reset_demo_data():
    """Reset demo data - only for development"""
    try:
        # Clear all data
        db.session.query(Message).delete()
        db.session.query(Match).delete()
        db.session.query(Swipe).delete()
        db.session.query(PointTransaction).delete()
        db.session.query(Profile).delete()
        db.session.query(User).delete()
        
        db.session.commit()
        
        return jsonify({'message': 'Demo data reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'GuideSwipe API is running'
    }), 200
