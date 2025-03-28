from datetime import datetime
import json
from app.models import db

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)  # Path ke file CSV hasil analisis
    result_file = db.Column(db.String(255), nullable=True)  # Path ke file hasil analisis
    total_tweets = db.Column(db.Integer, default=0)
    positive_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    positive_percent = db.Column(db.Float, default=0.0)
    neutral_percent = db.Column(db.Float, default=0.0)
    negative_percent = db.Column(db.Float, default=0.0)
    topics = db.Column(db.Text, nullable=True)  # JSON string
    hashtags = db.Column(db.Text, nullable=True)  # JSON string
    sentiment_plot = db.Column(db.Text, nullable=True)  # Base64 encoded
    word_cloud = db.Column(db.Text, nullable=True)  # Base64 encoded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key untuk relasi dengan User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def save_results(self, results):
        """Menyimpan hasil analisis dari JSON ke model"""
        if not results:
            return
            
        # Simpan statistik dasar
        self.total_tweets = results.get('total_tweets', 0)
        self.positive_count = results.get('positive_count', 0)
        self.neutral_count = results.get('neutral_count', 0)
        self.negative_count = results.get('negative_count', 0)
        self.positive_percent = results.get('positive_percent', 0.0)
        self.neutral_percent = results.get('neutral_percent', 0.0)
        self.negative_percent = results.get('negative_percent', 0.0)
        
        # Simpan topics dan hashtags sebagai JSON
        if 'topics' in results:
            self.topics = json.dumps(results['topics'])
        
        if 'top_hashtags' in results:
            self.hashtags = json.dumps(results['top_hashtags'])
            
        # Simpan gambar sebagai base64
        if 'sentiment_plot' in results:
            self.sentiment_plot = results['sentiment_plot']
            
        if 'word_cloud' in results:
            self.word_cloud = results['word_cloud']
    
    def get_topics(self):
        """Mengambil topics sebagai list of dict"""
        if not self.topics:
            return []
        return json.loads(self.topics)
    
    def get_hashtags(self):
        """Mengambil hashtags sebagai list of dict"""
        if not self.hashtags:
            return []
        return json.loads(self.hashtags)
    
    def to_dict(self):
        """Convert object to dictionary for JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'total_tweets': self.total_tweets,
            'positive_count': self.positive_count,
            'neutral_count': self.neutral_count,
            'negative_count': self.negative_count,
            'positive_percent': self.positive_percent,
            'neutral_percent': self.neutral_percent,
            'negative_percent': self.negative_percent,
            'topics': self.get_topics(),
            'hashtags': self.get_hashtags(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def __repr__(self):
        return f'<Analysis {self.title}>'