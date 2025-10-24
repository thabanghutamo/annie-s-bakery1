"""Background scheduler for timed tasks like publishing scheduled blog posts"""
import threading
import time
from datetime import datetime
from utils.json_store import read_json, write_json

def check_scheduled_posts():
    """Check for and publish any scheduled blog posts"""
    while True:
        try:
            posts = read_json('blog.json', [])
            now = datetime.now()
            updated = False
            
            for post in posts:
                # Skip if already published or no publish_date
                if post.get('published') or 'publish_date' not in post:
                    continue
                
                # Try parse publish date
                try:
                    publish_date = datetime.fromisoformat(post['publish_date'])
                    if now >= publish_date:
                        post['published'] = True
                        updated = True
                except (ValueError, TypeError):
                    continue
            
            if updated:
                write_json('blog.json', posts)
                
        except Exception as e:
            print('Scheduler error:', str(e))
            
        # Sleep for 1 minute before next check
        time.sleep(60)

def start_scheduler():
    """Start the background scheduler thread"""
    thread = threading.Thread(target=check_scheduled_posts, daemon=True)
    thread.start()
    return thread