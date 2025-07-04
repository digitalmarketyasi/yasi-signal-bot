import sqlite3
from datetime import datetime, timedelta
import uuid

# ---------- INIT ----------
def init_db():
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()

    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            ref_by TEXT
        )
    ''')

    # جدول اشتراک
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            start_date TEXT,
            end_date TEXT
        )
    ''')

    # جدول هش‌های تراکنش
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tx_hashes (
            tx TEXT PRIMARY KEY
        )
    ''')

    # جدول شانس‌های خریداری‌شده
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chances (
            user_id INTEGER,
            code TEXT
        )
    ''')

    # جدول شانس‌های رفرال
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ref_chances (
            user_id INTEGER,
            code TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ---------- USER ----------
def add_user(user_id, ref_by=None):
    if get_user(user_id) is None:
        conn = sqlite3.connect('lottery.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, ref_by) VALUES (?, ?)', (user_id, ref_by))
        conn.commit()

        # اگر کاربر جدید از رفرال استفاده کرده
        if ref_by:
            inviter = int(ref_by)
            refs = get_total_ref_count(inviter)
            if (refs + 1) % 3 == 0:  # هر 3 نفر = 1 شانس
                code = str(uuid.uuid4())[:8]
                cursor.execute('INSERT INTO ref_chances (user_id, code) VALUES (?, ?)', (inviter, code))
                conn.commit()

        conn.close()

def get_user(user_id):
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# ---------- SUBSCRIPTION ----------
def update_subscription(user_id, duration_days):
    start = datetime.now()
    end = start + timedelta(days=duration_days)
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO subscriptions (user_id, start_date, end_date) VALUES (?, ?, ?)', (
        user_id, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    ))
    conn.commit()
    conn.close()

def get_subscription_info(user_id):
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('SELECT start_date, end_date FROM subscriptions WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        start_date = datetime.strptime(row[0], "%Y-%m-%d")
        end_date = datetime.strptime(row[1], "%Y-%m-%d")
        return {
            "start": row[0],
            "end": row[1],
            "active": start_date <= datetime.now() <= end_date
        }
    else:
        return {"active": False}

# ---------- TRANSACTION ----------
def check_tx_hash(tx):
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tx_hashes WHERE tx = ?', (tx,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_tx_hash(tx):
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tx_hashes (tx) VALUES (?)', (tx,))
    conn.commit()
    conn.close()

# ---------- CHANCE ----------
def add_lottery_chance(user_id, tx):
    code = str(uuid.uuid4())[:8]
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chances (user_id, code) VALUES (?, ?)', (user_id, code))
    conn.commit()
    conn.close()
    return code

def get_user_chances(user_id):
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('SELECT code FROM chances WHERE user_id = ?', (user_id,))
    codes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return codes

# ---------- REFERRAL ----------
def generate_ref_link(user_id):
    return str(user_id)

def get_user_ref_chances(user_id):
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('SELECT code FROM ref_chances WHERE user_id = ?', (user_id,))
    codes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return codes

def get_total_ref_count(user_id):
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE ref_by = ?', (str(user_id),))
    count = cursor.fetchone()[0]
    conn.close()
    return count
