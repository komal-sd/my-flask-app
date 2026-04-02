from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from datetime import datetime
import logging

# Setup logging (DevOps perspective: monitor what's happening)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# DATABASE CONNECTION (from environment variable)
# DevOps will set: DATABASE_URL=postgresql://user:pass@rds-host/db
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/tasks_db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Model: Tasks table
class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = db.Column(db.String(100), nullable=True)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high

# HEALTH CHECK ENDPOINT (DevOps uses this!)
# ECS will call this every 30 seconds
# If app doesn't respond → ECS restarts the container
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - used by ECS"""
    try:
        # Check if database is accessible
        db.session.execute(text('SELECT 1'))
        logger.info("Health check passed")
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# API ENDPOINTS

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Get all tasks"""
    try:
        tasks = Task.query.all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'assigned_to': task.assigned_to,
            'created_at': task.created_at.isoformat()
        } for task in tasks]), 200
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get single task by ID"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'assigned_to': task.assigned_to,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create new task"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Create task
        task = Task(
            title=data.get('title'),
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            assigned_to=data.get('assigned_to', '')
        )
        
        # Save to database
        db.session.add(task)
        db.session.commit()
        
        logger.info(f"Task created: {task.id}")
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'message': 'Task created successfully'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'status' in data:
            task.status = data['status']
        if 'priority' in data:
            task.priority = data['priority']
        if 'assigned_to' in data:
            task.assigned_to = data['assigned_to']
        if 'description' in data:
            task.description = data['description']
        
        db.session.commit()
        logger.info(f"Task updated: {task_id}")
        
        return jsonify({'id': task.id, 'message': 'Task updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        logger.info(f"Task deleted: {task_id}")
        
        return jsonify({'message': 'Task deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get task statistics"""
    try:
        total = Task.query.count()
        completed = Task.query.filter_by(status='completed').count()
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        
        return jsonify({
            'total_tasks': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress
        }), 200
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Initialize database on startup
@app.before_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Run app
    # 0.0.0.0 = accessible from outside container
    # 5000 = port
    app.run(host='0.0.0.0', port=5000, debug=False)
