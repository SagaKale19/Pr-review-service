import sqlite3

API_KEY = "my-secret-api-key-123"


def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()


def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags


def average_age(users):
    total = 0
    for u in users:
        total += u["age"]
    return total / len(users)


def load_config(path):
    try:
        return open(path).read()
    except:
        pass