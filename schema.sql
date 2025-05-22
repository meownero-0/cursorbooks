CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE tour (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    summary TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    yandex_maps_url TEXT NOT NULL,
    points_of_interest TEXT NOT NULL,
    FOREIGN KEY(book_id) REFERENCES book(id)
);

CREATE TABLE completion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(tour_id) REFERENCES tour(id)
);

CREATE TABLE rating (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(tour_id) REFERENCES tour(id)
); 