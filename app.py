from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required
from flask_cors import CORS
from config import config
from models import db, User
import os

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Extensions
    db.init_app(app)
    CORS(app)
    
    # Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes import api
    app.register_blueprint(api)
    
    # Main routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/swipe')
    @login_required
    def swipe():
        return render_template('swipe.html')
    
    @app.route('/matches')
    @login_required
    def matches():
        return render_template('matches.html')
    
    @app.route('/chat/<int:match_id>')
    @login_required
    def chat(match_id):
        return render_template('chat.html', match_id=match_id)
    
    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
