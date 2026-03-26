from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost/notifications'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Redis connection for job queue
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# Database Model
class NotificationJob(db.Model):
    __tablename__ = 'notification_jobs'
    
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, sent, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    retry_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)

# API Endpoints

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """
    Submit a notification job
    Request: {
        "email": "user@example.com",
        "subject": "Hello",
        "body": "This is a test email"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ('email', 'subject', 'body')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create job
        job_id = str(uuid.uuid4())
        job = NotificationJob(
            id=job_id,
            email=data['email'],
            subject=data['subject'],
            body=data['body'],
            status='pending'
        )
        
        # Save to database
        db.session.add(job)
        db.session.commit()
        
        # Push to Redis queue
        redis_client.rpush('notification_queue', json.dumps({
            'job_id': job_id,
            'email': data['email'],
            'subject': data['subject'],
            'body': data['body']
        }))
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<job_id>', methods=['GET'])
def get_notification_status(job_id):
    """Get status of a notification job"""
    try:
        job = NotificationJob.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({
            'job_id': job.id,
            'email': job.email,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'updated_at': job.updated_at.isoformat(),
            'retry_count': job.retry_count,
            'error_message': job.error_message
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/stats', methods=['GET'])
def get_stats():
    """Get statistics about notifications"""
    try:
        total = NotificationJob.query.count()
        sent = NotificationJob.query.filter_by(status='sent').count()
        pending = NotificationJob.query.filter_by(status='pending').count()
        failed = NotificationJob.query.filter_by(status='failed').count()
        
        queue_length = redis_client.llen('notification_queue')
        
        return jsonify({
            'total_jobs': total,
            'sent': sent,
            'pending': pending,
            'failed': failed,
            'queue_length': queue_length
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)
