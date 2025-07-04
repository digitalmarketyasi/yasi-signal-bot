import sqlite3
from datetime import datetime, timedelta
import random
import string

DB_NAME = "lottery.db"

# ---------- INIT ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        ref_code TEXT,
        joined_at TEXT
    )
    ''')

    # Subscription
    c.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        start TEXT,
        end TEXT
    )
    ''')

    # Lottery chances
    c.execute('''
    CREATE TABLE IF NOT EXISTS chances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        chance_code TEXT,
        type TEXT, -- 'buy' or 'ref'
        created_at TEXT
    )
    ''')

    # Used TX hashes
    c.execute('''
    CREATE TABLE IF NOT EXISTS tx_hashes (
        hash TEXT PRIMARY KEY
    )
    ''')

    # Referrals
    c.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER,
        created_at TEXT
    )
    ''')

    conn.commit()
    conn.close()

# ---------- USERS ----------
def add_user(user_id, ref_code=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = c.fetchone()
    if not exists:
        joined_at = datetime.utcnow().isoformat()
        c.execute("INSERT INTO users (user_id, ref_code, joined_at) VALUES (?, ?, ?)", (user_id, ref_code, joined_at))
        conn.commit()

        # ثبت ارجاع (اگه ref_code معتبر باشه)
        if ref_code and ref_code.isdigit():
            referrer_id = int(ref_code)
            if referrer_id != user_id:
                c.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (referrer_id,))
                if c.fetchone()[0]:
                    # آیا قبلاً ثبت نشده؟
                    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND referred_id = ?", (referrer_id, user_id))
                    if c.fetchone()[0] == 0:
                        c.execute("INSERT INTO referrals (referrer_id, referred_id, created_at) VALUES (?, ?, ?)",
                                  (referrer_id, user_id, joined_at))
                        conn.commit()
    conn.close()

# ---------- REFERRALS ----------
def get_total_ref_count(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_user_ref_chances(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # تعداد کامل دعوت‌ها
    c.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    count = c.fetchone()[0]

    # چند شانس؟
    full_sets = count // 3
    c.execute("SELECT chance_code FROM chances WHERE user_id = ? AND type = 'ref'", (user_id,))
    existing = [r[0] for r in c.fetchall()]

    # تولید شانس‌های جدید (اگه نیاز بود)
    new_codes = []
    while len(existing) < full_sets:
        code = generate_code()
        c.execute("INSERT INTO chances (user_id, chance_code, type, created_at) VALUES (?, ?, 'ref', ?)",
                  (user_id, code, datetime.utcnow().isoformat()))
        new_codes.append(code)
        existing.append(code)
    conn.commit()
    conn.close()
    return existing

# ---------- CHANCES ----------
def add_lottery_chance(user_id, tx_hash):
    code = generate_code()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO chances (user_id, chance_code, type, created_at) VALUES (?, ?, 'buy', ?)",
              (user_id, code, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return code

def get_user_chances(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT chance_code FROM chances WHERE user_id = ? AND type = 'buy'", (user_id,))
    codes = [row[0] for row in c.fetchall()]
    conn.close()
    return codes

# ---------- TX HASHES ----------
def check_tx_hash(tx_hash):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM tx_hashes WHERE hash = ?", (tx_hash,))
    exists = c.fetchone()
    conn.close()
    return bool(exists)

def save_tx_hash(tx_hash):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tx_hashes (hash) VALUES (?)", (tx_hash,))
    conn.commit()
    conn.close()

# ---------- SUBSCRIPTION ----------
def update_subscription(user_id, duration_days):
    start = datetime.utcnow()
    end = start + timedelta(days=duration_days)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO subscriptions (user_id, start, end) VALUES (?, ?, ?)",
              (user_id, start.isoformat(), end.isoformat()))
    conn.commit()
    conn.close()

def get_subscription_info(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT start, end FROM subscriptions WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        start, end = row
        now = datetime.utcnow()
        active = datetime.fromisoformat(end) > now
        return {
            'active': active,
            'start': start,
            'end': end
        }
    else:
        return {'active': False}

# ---------- GENERATE REF LINK ----------
def generate_ref_link(user_id):
    return str(user_id)

# ---------- CODE GENERATOR ----------
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
