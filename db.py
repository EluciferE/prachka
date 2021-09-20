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
                       (chat_id text, username text UNIQUE, status text, tmp text)''')
cur.execute('''CREATE TABLE IF NOT EXISTS messages
                       (username text, value text)''')
cur.execute('''CREATE TABLE IF NOT EXISTS notes
                       (username text, date text, day text, time text, machine text, value text, cell text)''')
cur.execute('''CREATE TABLE IF NOT EXISTS signup
                       (username text, date text)''')


def insert_signup(username, date):
    try:
        with lock:
            cur.execute('''INSERT INTO signup VALUES ((?), (?))''', (username, date))
        con.commit()
    except Exception as e:
        db_logger.error(e)


def get_signups():
    try:
        with lock:
            req = cur.execute('''SELECT * FROM signup''')
        return [x for x in req]
    except Exception as e:
        db_logger.error(e)


def get_signup(username):
    try:
        with lock:
            req = cur.execute('''SELECT * FROM signup WHERE username=(?)''', (username,))
        return [x for x in req]
    except Exception as e:
        db_logger.error(e)


def accept_signup(username):
    try:
        with lock:
            cur.execute('''DELETE FROM signup WHERE username=(?)''', (username,))
        con.commit()
    except Exception as e:
        db_logger.error(e)


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
            ans = cur.execute('''SELECT username FROM users where status != "New" and status != "AskAllow"''')
        return [x for x in ans]
    except Exception as e:
        db_logger.error(e)


def get_chat_id(username):
    while True:
        try:
            with lock:
                ans = cur.execute('''SELECT chat_id FROM users WHERE username=(?)''', (username,))
            ans = [x for x in ans]
            db_logger.info(f"get_chat_id: {username}")
            if ans:
                return list(ans[0])[0]
            return []
        except Exception as e:
            db_logger.error(e)


def user_status(username):
    while True:
        try:
            with lock:
                ans = cur.execute('''SELECT status FROM users WHERE username=(?)''', (username,))
            ans = [x for x in ans]
            if ans:
                return ans[0][0]
            return []
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
        db_logger.error(e + f"args: {username} - {status}")


def add_user(chat_id, username):
    try:
        with lock:
            cur.execute('''INSERT INTO users VALUES ((?), (?), (?), (?))''', (chat_id, username, 'New', ''))
        con.commit()
    except Exception as e:
        db_logger.error(e)


def get_tmp(username):
    try:
        with lock:
            tmp = cur.execute('''Select tmp from users where username=(?)''', (username,))
            tmp = [x for x in tmp]
            if tmp:
                return list(tmp[0])[0]
            return []
    except Exception as e:
        db_logger.error(e)


def change_tmp(username, tmp):
    try:
        with lock:
            cur.execute('''UPDATE users SET tmp=(?) WHERE username=(?)''', (tmp, username))
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


def make_note(username, place, value):
    db_logger.info(f"[SQL] {username} : {place} : {value}")
    try:
        with lock:
            cur.execute("""INSERT INTO notes VALUES ((?), (?), (?), (?), (?), (?), (?))""",
                        (username, place["date"], place["day"], place["time"], place["machine"], value, place["cell"]))
            con.commit()
    except Exception as e:
        db_logger.error(e)


def delete_note(username, date):
    try:
        with lock:
            cur.execute('''DELETE FROM notes WHERE username=(?) AND date=(?)''', (username, date))
            con.commit()
    except Exception as e:
        db_logger.error(e)


def get_notes(username):
    try:
        with lock:
            notes = cur.execute('''SELECT * FROM notes WHERE username=(?)''', (username,))
            con.commit()
            notes = [x for x in notes]
            return notes
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


def all_notes():
    try:
        with lock:
            ans = cur.execute('''SELECT * FROM notes''')
            return [x for x in ans]
    except Exception as e:
        db_logger.error(e)
