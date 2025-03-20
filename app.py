from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://root:root@localhost/pastebin')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Paste(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    views = db.Column(db.Integer, default=0)

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Date, nullable=False)
    total_views = db.Column(db.Integer, default=0)
    total_pastes = db.Column(db.Integer, default=0)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/paste', methods=['POST'])
def create_paste():
    content = request.form.get('content')
    expiration = request.form.get('expiration')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    # Generate unique ID
    paste_id = secrets.token_urlsafe(12)
    
    # Calculate expiration time if specified
    expires_at = None
    if expiration:
        try:
            hours = int(expiration)
            expires_at = datetime.utcnow() + timedelta(hours=hours)
        except ValueError:
            return jsonify({'error': 'Invalid expiration time'}), 400
    
    # Create new paste
    paste = Paste(
        id=paste_id,
        content=content,
        expires_at=expires_at
    )
    
    db.session.add(paste)
    
    # Update analytics
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    analytics = Analytics.query.filter_by(month=current_month).first()
    
    if not analytics:
        analytics = Analytics(month=current_month, total_pastes=1)
        db.session.add(analytics)
    else:
        analytics.total_pastes += 1
    
    db.session.commit()
    
    return jsonify({
        'url': url_for('view_paste', paste_id=paste_id, _external=True),
        'paste_id': paste_id
    })

@app.route('/<paste_id>')
def view_paste(paste_id):
    paste = Paste.query.get_or_404(paste_id)
    
    # Check if paste has expired
    if paste.expires_at and paste.expires_at < datetime.utcnow():
        db.session.delete(paste)
        db.session.commit()
        abort(404)
    
    # Update view count and analytics
    paste.views += 1
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    analytics = Analytics.query.filter_by(month=current_month).first()
    
    if not analytics:
        analytics = Analytics(month=current_month, total_views=1)
        db.session.add(analytics)
    else:
        analytics.total_views += 1
    
    db.session.commit()
    
    return render_template('view.html', paste=paste)

@app.route('/analytics')
def view_analytics():
    analytics = Analytics.query.order_by(Analytics.month.desc()).all()
    return render_template('analytics.html', analytics=analytics)

def cleanup_expired_pastes():
    with app.app_context():
        expired_pastes = Paste.query.filter(
            Paste.expires_at.isnot(None),
            Paste.expires_at < datetime.utcnow()
        ).all()
        
        for paste in expired_pastes:
            db.session.delete(paste)
        
        db.session.commit()

# Initialize scheduler for cleanup task
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_pastes, 'interval', hours=1)
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 