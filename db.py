import sqlite3
import os.path
import threading
import logging

# LOGGING
FORMAT = '[%(asctime)s]- [%(filename)s:%(lineno)s - %(funcName)20s() ] - [%(levelname)s] - %(message)s'
db_logs = logging.FileHandler('logs/db.log')
db_logs.setFormatter(logging.Formatter(FORMAT))
logging.basicConfig(level=logging.INFO)

db_logger = logging.getLogger('db')
db_logger.addHandler(db_logs)
db_logger.propagate = False

lock = threading.Lock()

con = sqlite3.connect('main.db', check_same_thread=False)
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS requests
                       (username text UNIQUE, day text, time text, machine text, value text)''')
cur.execute('''CREATE TABLE IF NOT EXISTS users
                       (chat_id text, username text UNIQUE, status text)''')
cur.execute('''CREATE TABLE IF NOT EXISTS messages
                       (username text, value text)''')
cur.execute('''CREATE TABLE IF NOT EXISTS notes
                       (username text, date text, day text, time text, machine text, value text, cell text)''')


def insert_request(username, request):
    try:
        with lock:
            cur.execute('''INSERT INTO requests VALUES 
                       ((?), (?), (?), (?), (?))''', (username, request['day'],
                                                      request['time'], request['machine'],
                                                      request['value']))
        con.commit()
    except Exception as e:
        db_logger.error(e)


def get_requests():
    try:
        with lock:
            ans = cur.execute('''SELECT * FROM requests''')
        return [row for row in ans]
    except Exception as e:
        db_logger.error(e)


def get_request(username):
    try:
        with lock:
            ans = cur.execute('''SELECT * FROM requests WHERE username=(?)''', (username,))
        return [x for x in ans]
    except Exception as e:
        db_logger.error(e)


def get_users():
    try:
        with lock:
            ans = cur.execute('''SELECT * FROM users''')
        return [x for x in ans]
    except Exception as e:
        db_logger.error(e)


def get_chat_id(username):
    try:
        with lock:
            ans = cur.execute('''SELECT chat_id FROM users WHERE username=(?)''', (username,))
        return [x for x in ans]
    except Exception as e:
        db_logger.error(e)


def user_status(username):
    try:
        with lock:
            ans = cur.execute('''SELECT status FROM users WHERE username=(?)''', (username,))
        return [x for x in ans]
    except Exception as e:
        print(e)


def delete_request(username):
    try:
        with lock:
            cur.execute('''DELETE FROM requests WHERE username=(?)''', (username,))
        con.commit()
    except Exception as e:
        db_logger.error(e)


def change_status(username, status):
    try:
        with lock:
            cur.execute('''UPDATE users SET status=(?) WHERE username=(?)''', (status, username))
        con.commit()
    except Exception as e:
        db_logger.error(e)


def add_user(chat_id, username):
    try:
        with lock:
            cur.execute('''INSERT INTO users VALUES ((?), (?), (?))''', (chat_id, username, 'Not logged'))
        con.commit()
    except Exception as e:
        db_logger.error(e)


def add_message(username, text):
    try:
        with lock:
            cur.execute('''INSERT INTO messages VALUES ((?), (?))''', (username, text))
        con.commit()
    except Exception as e:
        db_logger.error(e)


def get_messages():
    try:
        with lock:
            messages = cur.execute('''SELECT * FROM messages''')
            return [x for x in messages]
    except Exception as e:
        db_logger.error(e)


def remove_message(username, msg):
    try:
        with lock:
            cur.execute('''DELETE FROM messages WHERE username=(?) AND value=(?)''',
                        (username, msg))
            con.commit()
    except Exception as e:
        db_logger.error(e)


def made_note(username, place, value):
    db_logger.info(f"[SQL] {username} : {place} : {value}")
    try:
        with lock:
            cur.execute("""INSERT INTO notes VALUES ((?), (?), (?), (?), (?), (?), (?))""",
                        (username, place["date"], place["day"], place["time"], place["machine"], value, place["cell"]))
            con.commit()
    except Exception as e:
        db_logger.error(e)


def delete_note(username):
    try:
        with lock:
            cur.execute('''DELETE FROM notes WHERE username=(?)''', (username,))
            con.commit()
    except Exception as e:
        db_logger.error(e)


def get_note(username):
    try:
        with lock:
            user = cur.execute('''SELECT * FROM notes WHERE username=(?)''', (username,))
            con.commit()
            user = [x for x in user]
            if user:
                user = user[0]
            return user
    except Exception as e:
        db_logger.error(e)


def note_by_time(date, time_):
    try:
        with lock:
            users = cur.execute('''SELECT username FROM notes WHERE time=(?) AND date=(?)''', (time_, date))
            con.commit()
            return [x for x in users]
    except Exception as e:
        db_logger.error(e)


def note_by_date(date):
    try:
        with lock:
            users = cur.execute('''SELECT username FROM notes WHERE date=(?)''', (date,))
            con.commit()
            return [x for x in users]
    except Exception as e:
        db_logger.error(e)
