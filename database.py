import sqlite3

DATABASE = "database.db"

def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            host_id INTEGER NOT NULL,
            max_players INTEGER DEFAULT 8,
            rounds INTEGER DEFAULT 3,
            draw_time INTEGER DEFAULT 80,
            current_round INTEGER DEFAULT 0,
            status TEXT DEFAULT 'waiting',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_private INTEGER DEFAULT 0
        );
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS room_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room INTEGER NOT NULL,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE (room, name)
        );
    ''')
    conn.commit()
    conn.close()

def make_room(name, host_id):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO rooms (name, host_id)
            VALUES (?, ?)
        ''', (name, host_id))
        
        room_id = c.lastrowid
        conn.commit()
        
        c.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        data = c.fetchone()
        return [room_id, data]
    
    except Exception as e:
        print(f"[make_room ERROR] {e}")
        return False
    
    finally:
        conn.close()

def remove_old_rooms(hours=5):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # ✅ Get old room IDs
        c.execute("SELECT id FROM rooms WHERE created_at <= datetime('now', ?)", (f'-{hours} hours',))
        old_rooms = c.fetchall()

        for (room_id,) in old_rooms:
            # Delete all users in that room
            c.execute("DELETE FROM room_users WHERE room = ?", (room_id,))
            
            # Delete the room itself
            c.execute("DELETE FROM rooms WHERE id = ?", (room_id,))

        removed = len(old_rooms)  # number of rooms removed
        conn.commit()
        return removed

    except Exception as e:
        print(f"[remove_old_rooms ERROR] {e}")
        return False

    finally:
        conn.close()

def addToRoom(name, user_id, room):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # ✅ Check if room exists
        c.execute("SELECT id FROM rooms WHERE name = ?", (room,))
        room_row = c.fetchone()
        if not room_row:
            print(f"[addToRoom ERROR] Room '{room}' does not exist")
            return [False, f"Room '{room}' does not exist"]

        room_id = room_row[0]

        # ✅ Insert user into the room
        c.execute('''
            INSERT INTO room_users (room, name, user_id)
            VALUES (?, ?, ?)
        ''', (room_id, name, user_id))

        conn.commit()
        return [name, room]

    except Exception as e:
        print(f"[addToRoom ERROR] {e}")
        return [False, False]

    finally:
        conn.close()

# Setup: tables first, then cleanup old rooms
create_table()
remove_old_rooms()
