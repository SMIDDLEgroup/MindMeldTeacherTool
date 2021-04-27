from datetime import datetime
import random
import sqlite3

datetime_format = "%Y-%m-%d %H:%M:%S"
parsing_format = "%Y-%m-%dT%H:%M"

db = sqlite3.connect('database.db', check_same_thread=False)
cur = db.cursor()

def create_database():
    cur.execute("""CREATE TABLE IF NOT EXISTS service_plan(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT UNIQUE,
       description TEXT,
       price INT);
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT UNIQUE,
       first_name TEXT,
       patronimic TEXT,
       last_name TEXT,
       city TEXT,
       street TEXT,
       house_number TEXT,
       apartment_number TEXT,
       balance INT,
       last_payment_date TEXT,
       last_payment_amount INT,
       service_plan_id INT,
       repair INT,
       credit INT,
       technical_scheduled TEXT,
       FOREIGN KEY(service_plan_id) REFERENCES service_plan(id));
    """)
    db.commit()

user_fields = ['id', 'username', 'first_name', 'patronimic', 'last_name', 'city', 'street', 'house_number',
               'apartment_number', 'balance', 'last_payment_date', 'last_payment_amount', 'service_plan_id',
               'repair', 'credit', 'technical_scheduled']

service_plan_fields = ['id', 'name', 'description', 'price']

def get_user(username):
    cur.execute('select * from users WHERE username = ?;', (username,))
    record = cur.fetchone()
    if record:
        res = {k: v for k, v in zip(user_fields, record)}
        res['repair'] = bool(res['repair'])
        if res['last_payment_date']:
            res['last_payment_date'] = datetime.strptime(res['last_payment_date'], datetime_format)
        if res['technical_scheduled']:
            res['technical_scheduled'] = datetime.strptime(res['technical_scheduled'], datetime_format)
        return res

def create_user(username, balance=1234, repair=False):
    if not username:
        username = 'user_' + str(random.randint(0, 10000000))
    cur.execute('INSERT INTO users (username, balance, repair) VALUES (?, ?, ?);', (username, balance, repair))
    db.commit()
    return get_user(username)

def get_user_data(username):
    user = get_user(username)
    return user if user else create_user(username)

def set_credit_flag(user_id, value):
    cur.execute('UPDATE users SET credit = ? WHERE id = ?;', (int(value), user_id))
    db.commit()


def get_service_plan(id):
    cur.execute('select * from service_plan WHERE id = ?;', (id,))
    record = cur.fetchone()
    if record:
        return {k: v for k, v in zip(service_plan_fields, record)}

def call_home_service(user_id, day, hour):
    day = datetime.strptime(day[:16], parsing_format)
    hour = datetime.strptime(hour[:16], parsing_format)
    dt = day.replace(hour=hour.hour, minute=hour.minute)
    cur.execute('UPDATE users SET technical_scheduled = ? WHERE id = ?;', (dt.strftime(datetime_format),
                                                                           user_id))
    db.commit()