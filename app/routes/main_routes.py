import os
from flask import Blueprint, current_app, render_template, flash, redirect, url_for, session
from flask_login import login_required
from app.services.sentiment_analysis import load_sentiment_model

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    # Cek apakah model terlatih ada
    model_path = current_app.config['MODEL_PATH']
    if not os.path.exists(model_path):
        flash("PERINGATAN: Model terlatih tidak ditemukan di path models/indobert_sentiment_best.pt. Aplikasi mungkin tidak berfungsi dengan benar.", "warning")
    
    # Cek jika ada data dari riwayat yang perlu ditampilkan
    from_history = session.get('from_history', False)
    analysis_data = session.get('analysis_data', None)
    
    return render_template('index.html', from_history=from_history, analysis_data=analysis_data)

@main_bp.route('/clear_session')
@login_required
def clear_session():
    """Membersihkan session untuk membuat analisis baru"""
    if 'analysis_file' in session:
        del session['analysis_file']
    if 'analysis_context' in session:
        del session['analysis_context']
    if 'from_history' in session:
        del session['from_history']
    if 'analysis_data' in session:
        del session['analysis_data']
    
    flash("Session dibersihkan. Anda dapat membuat analisis baru.", "info")
    return redirect(url_for('main.index'))