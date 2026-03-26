import redis
import json
import time
import logging
from datetime import datetime
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost/notifications'
)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def process_job(job_data):
    """
    Simulate sending email notification
    In real world: integrate with SendGrid, AWS SES, etc.
    """
    try:
        logger.info(f"Processing job: {job_data['job_id']}")
        
        # Simulate email sending (takes 2 seconds)
        time.sleep(2)
        
        # In production: actually send email here
        # send_email(job_data['email'], job_data['subject'], job_data['body'])
        
        logger.info(f"Job {job_data['job_id']} completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Failed to process job: {str(e)}")
        return False

def worker():
    """
    Main worker loop
    Continuously processes jobs from Redis queue
    """
    logger.info("Worker started...")
    
    while True:
        try:
            # Get job from queue (blocking)
            job_json = redis_client.blpop('notification_queue', timeout=10)
            
            if not job_json:
                logger.info("No jobs in queue, waiting...")
                continue
            
            job_data = json.loads(job_json[1])
            job_id = job_data['job_id']
            
            # Update status to processing
            logger.info(f"Processing: {job_id}")
            
            # Process the job
            success = process_job(job_data)
            
            if success:
                logger.info(f"Job {job_id} sent successfully")
            else:
                logger.error(f"Job {job_id} failed")
                # Could retry or push back to queue
        
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            time.sleep(5)  # Backoff before retry

if __name__ == '__main__':
    worker()
