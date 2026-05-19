from app.config import get_db_connection

def get_attendance_by_date(date):
    conn = get_db_connection()

    rows = conn.execute("""
        SELECT * FROM child_attendance
        WHERE attendance_date = ?
    """, (date,)).fetchall()

    conn.close()
    return rows