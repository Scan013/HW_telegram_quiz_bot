import aiosqlite
from config import DB_NAME

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        # состояние текущего квиза (индекс вопроса + счёт)
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state 
                            (user_id INTEGER PRIMARY KEY, 
                             question_index INTEGER,
                             score INTEGER DEFAULT 0)''')
        # последний результат игрока
        await db.execute('''CREATE TABLE IF NOT EXISTS user_stats 
                            (user_id INTEGER PRIMARY KEY, 
                             last_score INTEGER,
                             total_questions INTEGER DEFAULT 10)''')
        await db.commit()

async def update_quiz_state(user_id: int, index: int, score: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) 
                            VALUES (?, ?, ?)''', (user_id, index, score))
        await db.commit()

async def get_quiz_state(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index, score FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return (row[0], row[1]) if row else (0, 0)

async def save_final_result(user_id: int, score: int, total: int = 10):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT OR REPLACE INTO user_stats (user_id, last_score, total_questions) 
                            VALUES (?, ?, ?)''', (user_id, score, total))
        await db.commit()

async def get_last_result(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT last_score, total_questions FROM user_stats WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return (row[0], row[1]) if row else (None, 10)