import sqlite3
import threading
import logging


class DataBase:
    def __init__(self):
        self.con = sqlite3.connect('dataBase/main.db', check_same_thread=False)
        self.cur = self.con.cursor()
        self.lock = threading.Lock()

        # LOGGING
        FORMAT = '[%(asctime)s]- [%(filename)s:%(lineno)s - %(funcName)20s() ] - [%(levelname)s] - %(message)s'
        db_logs = logging.FileHandler('logs/db.log')
        db_logs.setFormatter(logging.Formatter(FORMAT))
        logging.basicConfig(level=logging.INFO)

        self.db_logger = logging.getLogger('db')
        self.db_logger.addHandler(db_logs)
        self.db_logger.propagate = False

        self.cur.execute('''CREATE TABLE IF NOT EXISTS requests
                               (username text UNIQUE, day text, time text, machine text, value text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
                               (chat_id text, username text UNIQUE, status text, tmp text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS notes
                               (username text, date text, day text, time text, machine text, value text, cell text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS signup
                               (username text, date text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS anti_spam
                                       (username text, flag text)''')

    def insert_signup(self, username, date):
        try:
            with self.lock:
                self.cur.execute('''INSERT INTO signup VALUES ((?), (?))''', (username, date))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def get_signups(self):
        try:
            with self.lock:
                req = self.cur.execute('''SELECT * FROM signup''')
                return [x for x in req]
        except Exception as e:
            self.db_logger.error(e)

    def get_signup(self, username):
        try:
            with self.lock:
                req = self.cur.execute('''SELECT * FROM signup WHERE username=(?)''', (username,))
                return [x for x in req]
        except Exception as e:
            self.db_logger.error(e)

    def accept_signup(self, username):
        try:
            with self.lock:
                self.cur.execute('''DELETE FROM signup WHERE username=(?)''', (username,))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def insert_request(self, username, request):
        try:
            with self.lock:
                self.cur.execute('''INSERT INTO requests VALUES 
                           ((?), (?), (?), (?), (?))''', (username, request['day'],
                                                          request['time'], request['machine'],
                                                          request['value']))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def get_requests(self):
        try:
            with self.lock:
                ans = self.cur.execute('''SELECT * FROM requests''')
                return [row for row in ans]
        except Exception as e:
            self.db_logger.error(e)

    def get_request(self, username):
        try:
            with self.lock:
                ans = self.cur.execute('''SELECT * FROM requests WHERE username=(?)''', (username,))
                return [x for x in ans]
        except Exception as e:
            self.db_logger.error(e)

    def get_users(self):
        try:
            with self.lock:
                ans = self.cur.execute(
                    '''SELECT username FROM users where status != "New" and status != "AskAllow" and status != "Banned"''')
                return [x for x in ans]
        except Exception as e:
            self.db_logger.error(e)

    def get_chat_id(self, username):
        while True:
            try:
                with self.lock:
                    ans = self.cur.execute('''SELECT chat_id FROM users WHERE username=(?)''', (username,))
                    ans = [x for x in ans]
                    self.db_logger.info(f"get_chat_id: {username}")
                    if ans:
                        return list(ans[0])[0]
                    return []
            except Exception as e:
                self.db_logger.error(e)

    def user_status(self, username):
        while True:
            try:
                with self.lock:
                    ans = self.cur.execute('''SELECT status FROM users WHERE username=(?)''', (username,))
                    ans = [x for x in ans]
                    if ans:
                        return ans[0][0]
                    return []
            except Exception as e:
                self.db_logger.error(e)

    def delete_request(self, username):
        try:
            with self.lock:
                self.cur.execute('''DELETE FROM requests WHERE username=(?)''', (username,))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def change_status(self, username, status):
        try:
            with self.lock:
                self.cur.execute('''UPDATE users SET status=(?) WHERE username=(?)''', (status, username))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e + f"args: {username} - {status}")

    def add_user(self, chat_id, username):
        try:
            with self.lock:
                self.cur.execute('''INSERT INTO users VALUES ((?), (?), (?), (?))''', (chat_id, username, 'New', ''))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def get_tmp(self, username):
        while True:
            try:
                with self.lock:
                    tmp = self.cur.execute('''Select tmp from users where username=(?)''', (username,))
                    tmp = [x for x in tmp]
                    if tmp:
                        return list(tmp[0])[0]
                    return []
            except Exception as e:
                self.db_logger.error(e)

    def change_tmp(self, username, tmp):
        try:
            with self.lock:
                self.cur.execute('''UPDATE users SET tmp=(?) WHERE username=(?)''', (tmp, username))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def add_message(self, username, text):
        try:
            with self.lock:
                self.cur.execute('''INSERT INTO messages VALUES ((?), (?))''', (username, text))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def get_messages(self):
        try:
            with self.lock:
                messages = self.cur.execute('''SELECT * FROM messages''')
                return [x for x in messages]
        except Exception as e:
            self.db_logger.error(e)

    def remove_message(self, username, msg):
        try:
            with self.lock:
                self.cur.execute('''DELETE FROM messages WHERE username=(?) AND value=(?)''',
                                 (username, msg))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def make_note(self, username, place, value):
        try:
            with self.lock:
                self.cur.execute("""INSERT INTO notes VALUES ((?), (?), (?), (?), (?), (?), (?))""",
                                 (username, place["date"], place["day"], place["time"], place["machine"], value,
                                  place["cell"]))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def delete_note_by_day(self, username, date):
        try:
            with self.lock:
                self.cur.execute('''DELETE FROM notes WHERE username=(?) AND date=(?)''', (username, date))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def delete_all_notes(self, username):
        try:
            with self.lock:
                self.cur.execute('''DELETE FROM notes WHERE username=(?)''', (username,))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def get_notes(self, username):
        try:
            with self.lock:
                notes = self.cur.execute('''SELECT * FROM notes WHERE username=(?)''', (username,))
                self.con.commit()
                notes = [x for x in notes]
                return notes
        except Exception as e:
            self.db_logger.error(e)

    def note_by_time(self, date, time_):
        try:
            with self.lock:
                users = self.cur.execute('''SELECT username FROM notes WHERE time=(?) AND date=(?)''', (time_, date))
                self.con.commit()
                return [x for x in users]
        except Exception as e:
            self.db_logger.error(e)

    def note_by_date(self, date):
        try:
            with self.lock:
                users = self.cur.execute('''SELECT username FROM notes WHERE date=(?)''', (date,))
                self.con.commit()
                return [x for x in users]
        except Exception as e:
            self.db_logger.error(e)

    def all_notes(self):
        try:
            with self.lock:
                ans = self.cur.execute('''SELECT * FROM notes''')
                return [x for x in ans]
        except Exception as e:
            self.db_logger.error(e)

    def banned_users(self):
        try:
            with self.lock:
                ans = self.cur.execute('''SELECT username FROM users where status="Banned"''')
                return [x for x in ans]
        except Exception as e:
            self.db_logger.error(e)

    def mark_as_announced(self, username, week):
        try:
            with self.lock:
                ans1 = self.cur.execute('''SELECT * FROM anti_spam WHERE username=(?)''', (username,))
                ans1 = [_ for _ in ans1]
                print(f"mark_as_announced {username}: {ans1}")
                if ans1:
                    self.cur.execute('''UPDATE anti_spam SET=(?) WHERE username=(?)''', (week, username))
                else:
                    self.cur.execute('''INSERT INTO anti_spam VALUES ((?), (?))''', (username, week))
                self.con.commit()
        except Exception as e:
            self.db_logger.error(e)

    def is_announced(self, username):
        try:
            with self.lock:
                ans1 = self.cur.execute('''SELECT flag FROM anti_spam WHERE username=(?)''', (username,))
                ans1 = [_ for _ in ans1]
                print(f"is_announced {username}: {ans1}")
                if not ans1:
                    return False
                return ans1[0][0]
        except Exception as e:
            self.db_logger.error(e)
