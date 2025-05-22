from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Book, Tour, Completion, Rating
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    view_all = request.args.get('view') == 'all'
    sort_by = request.args.get('sort', 'popularity')
    
    if view_all:
        # Get all books with their tours
        books = Book.query.join(Tour).all()
        
        # Sort books based on the selected criteria
        if sort_by == 'popularity':
            books.sort(key=lambda x: len(x.tours[0].completions) if x.tours else 0, reverse=True)
        else:  # sort_by == 'rating'
            books.sort(key=lambda x: (
                sum(r.score for r in x.tours[0].ratings) / len(x.tours[0].ratings)
                if x.tours and x.tours[0].ratings else 0
            ), reverse=True)
        
        return render_template('index.html',
                             view_all=True,
                             sort_by=sort_by,
                             all_books=books)
    
    if search_query:
        # Search in books by title or author
        books = Book.query.filter(
            db.or_(
                Book.title.ilike(f'%{search_query}%'),
                Book.author.ilike(f'%{search_query}%')
            )
        ).all()
        
        # Get tours for the found books
        book_ids = [book.id for book in books]
        tours = Tour.query.filter(Tour.book_id.in_(book_ids)).all()
        
        return render_template('index.html', 
                             search_query=search_query,
                             books=books,
                             tours=tours)
    
    # If no search query, show popular and top-rated tours
    last_month = datetime.datetime.now() - datetime.timedelta(days=30)
    popular_tours = db.session.query(Tour, db.func.count(Completion.id).label('completion_count'))\
        .join(Completion)\
        .filter(Completion.timestamp >= last_month)\
        .group_by(Tour.id)\
        .order_by(db.desc('completion_count'))\
        .limit(3)\
        .all()
    popular_tours = [tour for tour, _ in popular_tours]

    top_rated_tours = db.session.query(Tour, db.func.avg(Rating.score).label('avg_rating'))\
        .join(Rating)\
        .group_by(Tour.id)\
        .order_by(db.desc('avg_rating'))\
        .limit(3)\
        .all()
    top_rated_tours = [tour for tour, _ in top_rated_tours]

    return render_template('index.html', 
                         popular_tours=popular_tours, 
                         top_rated_tours=top_rated_tours)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Это имя пользователя уже занято')
            return redirect(url_for('register'))
        user = User(email=email, username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Пожалуйста, войдите.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вход выполнен успешно!')
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    tour = Tour.query.filter_by(book_id=book_id).first_or_404()
    
    # Get average rating if any exists
    avg_rating = None
    if tour.ratings:
        avg_rating = sum(r.score for r in tour.ratings) / len(tour.ratings)
    
    # Check if current user has completed this tour
    has_completed = False
    if current_user.is_authenticated:
        has_completed = Completion.query.filter_by(
            user_id=current_user.id,
            tour_id=tour.id
        ).first() is not None
    
    # Get user's rating if they've rated this tour
    user_rating = None
    if current_user.is_authenticated:
        rating = Rating.query.filter_by(
            user_id=current_user.id,
            tour_id=tour.id
        ).first()
        if rating:
            user_rating = rating.score
    
    # Parse points_of_interest if it's JSON
    points = None
    if tour.points_of_interest and tour.points_of_interest.startswith('['):
        try:
            points = json.loads(tour.points_of_interest)
        except Exception:
            points = None

    return render_template('book_detail.html', 
                         book=book, 
                         tour=tour, 
                         avg_rating=avg_rating,
                         has_completed=has_completed,
                         user_rating=user_rating,
                         points=points)

@app.route('/complete_tour/<int:tour_id>', methods=['POST'])
@login_required
def complete_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    # Check if already completed
    existing_completion = Completion.query.filter_by(
        user_id=current_user.id,
        tour_id=tour_id
    ).first()
    
    if not existing_completion:
        completion = Completion(
            user_id=current_user.id,
            tour_id=tour_id,
            timestamp=datetime.datetime.now()
        )
        db.session.add(completion)
        db.session.commit()
        flash('Тур отмечен как пройденный!')
    else:
        flash('Вы уже прошли этот тур!')
    
    return redirect(url_for('book_detail', book_id=tour.book_id))

@app.route('/rate_tour/<int:tour_id>', methods=['POST'])
@login_required
def rate_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    score = int(request.form.get('rating'))
    
    if not 1 <= score <= 10:
        flash('Неверная оценка')
        return redirect(url_for('book_detail', book_id=tour.book_id))
    
    # Check if user has already rated
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id,
        tour_id=tour_id
    ).first()
    
    if existing_rating:
        existing_rating.score = score
        existing_rating.timestamp = datetime.datetime.now()
    else:
        rating = Rating(
            user_id=current_user.id,
            tour_id=tour_id,
            score=score,
            timestamp=datetime.datetime.now()
        )
        db.session.add(rating)
    
    db.session.commit()
    flash('Спасибо за вашу оценку!')
    return redirect(url_for('book_detail', book_id=tour.book_id))

