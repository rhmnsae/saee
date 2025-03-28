import os
import pandas as pd
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user

from app.models import db
from app.models.analysis import Analysis

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
@login_required
def index():
    """Menampilkan halaman riwayat analisis"""
    return render_template('history/index.html', title='Riwayat Analisis')

@history_bp.route('/history/data')
@login_required
def get_history_data():
    """API untuk mendapatkan data riwayat analisis"""
    # Get query parameters for pagination and filtering
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Base query
    query = Analysis.query.filter_by(user_id=current_user.id)
    
    # Apply search filter if provided
    if search:
        query = query.filter(Analysis.title.ilike(f'%{search}%'))
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(Analysis, sort_by).desc())
    else:
        query = query.order_by(getattr(Analysis, sort_by).asc())
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepare response
    analyses = pagination.items
    total = pagination.total
    
    response = {
        'data': [analysis.to_dict() for analysis in analyses],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }
    
    return jsonify(response)

@history_bp.route('/history/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """Menampilkan detail analisis"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    
    # Load analysis result file if exists
    result_data = None
    if analysis.result_file and os.path.exists(analysis.result_file):
        try:
            df = pd.read_csv(analysis.result_file)
            # Convert to list of dictionaries for frontend
            tweets = []
            for _, row in df.iterrows():
                tweet = {
                    'username': row.get('username', ''),
                    'content': row.get('content', ''),
                    'date': row.get('date', ''),
                    'likes': row.get('likes', 0),
                    'retweets': row.get('retweets', 0),
                    'replies': row.get('replies', 0),
                    'predicted_sentiment': row.get('predicted_sentiment', ''),
                    'confidence': row.get('confidence', 0)
                }
                tweets.append(tweet)
                
            analysis_data = {
                'id': analysis.id,
                'title': analysis.title,
                'total_tweets': analysis.total_tweets,
                'positive_count': analysis.positive_count,
                'neutral_count': analysis.neutral_count,
                'negative_count': analysis.negative_count,
                'positive_percent': analysis.positive_percent,
                'neutral_percent': analysis.neutral_percent,
                'negative_percent': analysis.negative_percent,
                'topics': analysis.get_topics(),
                'top_hashtags': analysis.get_hashtags(),
                'sentiment_plot': analysis.sentiment_plot,
                'word_cloud': analysis.word_cloud,
                'tweets': tweets
            }
            
            # Save to session for other views to use
            request.session['analysis_context'] = {
                'title': analysis.title,
                'total_tweets': analysis.total_tweets,
                'positive_count': analysis.positive_count,
                'neutral_count': analysis.neutral_count,
                'negative_count': analysis.negative_count,
                'positive_percent': analysis.positive_percent,
                'neutral_percent': analysis.neutral_percent,
                'negative_percent': analysis.negative_percent,
                'top_hashtags': [h['tag'] for h in analysis.get_hashtags()[:5]] if analysis.get_hashtags() else [],
                'top_topics': [t['topic'] for t in analysis.get_topics()[:5]] if analysis.get_topics() else []
            }
            request.session['analysis_file'] = analysis.result_file
            
            return render_template('history/view.html', title=f'Analisis: {analysis.title}', 
                                 analysis=analysis, analysis_data=analysis_data)
                                 
        except Exception as e:
            flash(f'Gagal memuat data analisis: {str(e)}', 'danger')
            return redirect(url_for('history.index'))
    else:
        flash('File hasil analisis tidak ditemukan', 'warning')
        return redirect(url_for('history.index'))

@history_bp.route('/history/delete/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    """Menghapus analisis"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first_or_404()
    
    # Delete associated files
    if analysis.file_path and os.path.exists(analysis.file_path):
        try:
            os.remove(analysis.file_path)
        except:
            current_app.logger.warning(f"Failed to delete file: {analysis.file_path}")
    
    if analysis.result_file and os.path.exists(analysis.result_file):
        try:
            os.remove(analysis.result_file)
        except:
            current_app.logger.warning(f"Failed to delete file: {analysis.result_file}")
    
    # Delete from database
    db.session.delete(analysis)
    db.session.commit()
    
    flash('Analisis berhasil dihapus', 'success')
    return jsonify({'success': True})