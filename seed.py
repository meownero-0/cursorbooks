from app import app, db
from models import User, Book, Tour, Completion, Rating
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        # Clear existing data
        Rating.query.delete()
        Completion.query.delete()
        Tour.query.delete()
        Book.query.delete()
        User.query.delete()
        
        # Create test user
        user = User(
            email='test@example.com',
            username='testuser',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)
        
        # Create Russian classics about St. Petersburg
        books = [
            Book(
                title='Преступление и наказание',
                author='Фёдор Достоевский',
                description='Психологический роман, действие которого происходит в Санкт-Петербурге. История Родиона Раскольникова, бедного бывшего студента, который планирует убить старуху-процентщицу.'
            ),
            Book(
                title='Медный всадник',
                author='Александр Пушкин',
                description='Поэма, рассказывающая о наводнении 1824 года в Санкт-Петербурге и памятнике Петру Великому.'
            ),
            Book(
                title='Идиот',
                author='Фёдор Достоевский',
                description='Роман, действие которого происходит в Санкт-Петербурге, повествует о чистом и невинном князе Мышкине и его опыте в коррумпированном обществе.'
            ),
            Book(
                title='Белые ночи',
                author='Фёдор Достоевский',
                description='Повесть, действие которой происходит в Санкт-Петербурге во время белых ночей, рассказывает историю неразделённой любви.'
            ),
            Book(
                title='Пиковая дама',
                author='Александр Пушкин',
                description='Повесть, действие которой происходит в Санкт-Петербурге, рассказывает о молодом военном офицере, одержимом секретом выигрыша в карты.'
            )
        ]
        
        for book in books:
            db.session.add(book)
        
        db.session.commit()
        
        # Create tours for each book
        tours = [
            Tour(
                book_id=books[0].id,
                summary='Пройдите по следам Раскольникова по Санкт-Петербургу',
                duration_minutes=180,
                yandex_maps_url='https://yandex.ru/maps/st-petersburg/',
                points_of_interest='Сенная площадь, Дом Раскольникова, Полицейский участок, Сенной рынок'
            ),
            Tour(
                book_id=books[1].id,
                summary='Откройте для себя достопримечательности Санкт-Петербурга Пушкина',
                duration_minutes=120,
                yandex_maps_url='https://yandex.ru/maps/st-petersburg/',
                points_of_interest='Памятник Медный всадник, Сенатская площадь, Набережная Невы'
            ),
            Tour(
                book_id=books[2].id,
                summary='Исследуйте аристократический Санкт-Петербург "Идиота"',
                duration_minutes=150,
                yandex_maps_url='https://yandex.ru/maps/st-petersburg/',
                points_of_interest='Невский проспект, Елагин остров, Летний сад'
            ),
            Tour(
                book_id=books[3].id,
                summary='Почувствуйте романтический Санкт-Петербург "Белых ночей"',
                duration_minutes=90,
                yandex_maps_url='https://yandex.ru/maps/?rtext=59.9244,30.3186~59.9292,30.3197~59.9297,30.3207~59.9322,30.3081~59.9337,30.3061~59.9362,30.3021~59.9247,30.3042~59.9225,30.2987&rtt=pedestrian',
                points_of_interest='[{"name": "Сенная площадь", "lat": 59.9244, "lng": 30.3186}, {"name": "Кокушкин мост", "lat": 59.9292, "lng": 30.3197}, {"name": "Казначейская улица, 7", "lat": 59.9297, "lng": 30.3207}, {"name": "Синий мост", "lat": 59.9322, "lng": 30.3081}, {"name": "Исаакиевская площадь", "lat": 59.9337, "lng": 30.3061}, {"name": "Медный всадник", "lat": 59.9362, "lng": 30.3021}, {"name": "Крюков канал", "lat": 59.9247, "lng": 30.3042}, {"name": "Мост поцелуев", "lat": 59.9225, "lng": 30.2987}]'
            ),
            Tour(
                book_id=books[4].id,
                summary='Посетите игорные дома и аристократические особняки "Пиковой дамы"',
                duration_minutes=120,
                yandex_maps_url='https://yandex.ru/maps/st-petersburg/',
                points_of_interest='Зимний дворец, Эрмитаж, Миллионная улица'
            )
        ]
        
        for tour in tours:
            db.session.add(tour)
        
        db.session.commit()
        
        # Add completions and ratings
        now = datetime.now()
        last_month = now - timedelta(days=30)
        
        # Add completions for popular tours
        for i in range(5):  # 5 completions for Crime and Punishment tour
            completion = Completion(
                user_id=user.id,
                tour_id=tours[0].id,
                timestamp=last_month + timedelta(days=i)
            )
            db.session.add(completion)
        
        for i in range(3):  # 3 completions for The Bronze Horseman tour
            completion = Completion(
                user_id=user.id,
                tour_id=tours[1].id,
                timestamp=last_month + timedelta(days=i)
            )
            db.session.add(completion)
        
        # Add ratings for highest-rated tours
        ratings = [
            Rating(user_id=user.id, tour_id=tours[0].id, score=9, timestamp=now),
            Rating(user_id=user.id, tour_id=tours[0].id, score=10, timestamp=now),
            Rating(user_id=user.id, tour_id=tours[1].id, score=8, timestamp=now),
            Rating(user_id=user.id, tour_id=tours[2].id, score=9, timestamp=now),
            Rating(user_id=user.id, tour_id=tours[3].id, score=7, timestamp=now),
            Rating(user_id=user.id, tour_id=tours[4].id, score=8, timestamp=now)
        ]
        
        for rating in ratings:
            db.session.add(rating)
        
        db.session.commit()
        print("База данных успешно заполнена!")

if __name__ == '__main__':
    seed_database() 