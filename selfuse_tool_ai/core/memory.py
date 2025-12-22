import sqlite3
from pathlib import Path

class MemoryStore:
    def __init__(self, db_path: str = "memory.db"):
        # 確保資料目錄存在
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Initialize SQLite connection and create table if not exists
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)"
        )
        self.conn.commit()
        cur.close()

    def add(self, role: str, content: str):
        """Add a message to memory."""
        cur = self.conn.cursor()
        cur.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
        self.conn.commit()
        cur.close()

    def fetch_recent(self, limit: int = 10):
        """Fetch recent messages in chronological order."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = cur.fetchall()
        cur.close()
        # Reverse to return chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def close(self):
        """Close the SQLite connection."""
        if self.conn:
            self.conn.close()
