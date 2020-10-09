#!/usr/bin/python
import csv
import sqlite3

from datetime import datetime

current_year = "2020"

iso_dow_dict: dict = {
    "Mon": 1,
    "Tue": 2,
    "Wed": 3,
    "Thu": 4,
    "Fri": 5,
    "Sat": 6,
    "Sun": 7
}

if __name__ == "leaked_message_extractor":
    text_file_path = "Patriot-Coalition-PNW-Daily-Chatter-Scrapes.txt"
    csv_file_path = "extracted_files/Patriot-Coalition-PNW-Daily-Chatter-Scrapes.csv"
    sqlite_db_path = "extracted_files/patriot-coalition-pnw-daily-chatter-scrapes.sqlite"
else:
    text_file_path = "../Patriot-Coalition-PNW-Daily-Chatter-Scrapes.txt"
    csv_file_path = "../extracted_files/Patriot-Coalition-PNW-Daily-Chatter-Scrapes.csv"
    sqlite_db_path = "../extracted_files/patriot-coalition-pnw-daily-chatter-scrapes.sqlite"

fieldnames = ['dts', 'day', 'dow', 'avatar', 'message']


def create_sqlite_dbase_table_and_indexes(db_path):
    sql_stmts = list()
    sql_stmts.append("""
        CREATE TABLE IF NOT EXISTS messages (
            dts DATETIME NULL,
            day VARCHAR(10) NULL,
            dow INTEGER NULL,
            avatar TEXT NULL,
            message TEXT NULL
            )
    """)
    sql_stmts.append("CREATE INDEX IF NOT EXISTS ix_messages_dts ON messages (dts)")
    sql_stmts.append("CREATE INDEX IF NOT EXISTS ix_messages_avatar ON messages (avatar)")
    sql_stmts.append("DELETE FROM messages")

    with sqlite3.connect(db_path) as _conn:
        for sql_stmt in sql_stmts:
            _conn.execute(sql_stmt)
        _conn.commit()


def level_break_on_dts_change(cursor, csv_writer, avatar, message, dts, day, dow):
    # level-break on change of avatar value
    # outputting and then resetting the values
    if avatar is not None and message != "":
        print(f"dts: {dts}, day: {day}, dow: {dow}")
        print(f"avatar: {avatar}")
        print(f"message: {message.strip()}")
        cursor.execute("INSERT INTO messages (dts, day, dow, avatar, message) VALUES(?, ?, ?, ?, ?)",
                       [dts, day, dow, avatar, message.strip()])
        csv_writer.writerow([dts, day, dow, avatar, message])


def extract_leaked_messages():

    create_sqlite_dbase_table_and_indexes(sqlite_db_path)

    with sqlite3.connect(sqlite_db_path) as conn:
        cursor = conn.cursor()
        with open(text_file_path, "r", encoding="utf-8") as text_file:
            with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(fieldnames)
                avatar_encountered = False
                avatar = None
                message = ""
                dts = None
                day = None
                dow = None
                for text in text_file:
                    text = text.strip()

                    # if appropriate, obtain the full date-time stamp
                    try:
                        _d = datetime.strptime(text, "%b %d, %H:%M %p")
                        level_break_on_dts_change(cursor, csv_writer, avatar, message, dts, day, dow)
                        avatar = None
                        message = ""
                        dts = datetime.strptime(f"{current_year} {text}", "%Y %b %d, %I:%M %p")
                        day = dts.strftime("%a")
                        dow = dts.isoweekday()
                        continue  # go to next text row
                    except ValueError:
                        try:
                            _d = datetime.strptime(text, "%a, %I:%M %p")
                            level_break_on_dts_change(cursor, csv_writer, avatar, message, dts, day, dow)
                            avatar = None
                            message = ""
                            dts = datetime.strptime(text, "%a, %I:%M %p")
                            day = text[:3]
                            dow = iso_dow_dict[day]
                            continue  # go to next text row
                        except ValueError:
                            try:
                                _d = datetime.strptime(text, "%I:%M %p")
                                level_break_on_dts_change(cursor, csv_writer, avatar, message, dts, day, dow)
                                avatar = None
                                message = ""
                                dts = datetime.strptime(text, "%I:%M %p")
                                day = None
                                dow = dts.isoweekday()
                                continue  # go to next text row
                            except ValueError:
                                pass  # fall-through to code below as text is not in an expected date-time format

                    if text.strip() == "Avatar":
                        avatar_encountered = True
                        # level-break on change of avatar value
                        # outputting and then resetting the values
                        if avatar is not None and message != "":
                            level_break_on_dts_change(cursor, csv_writer, avatar, message, dts, day, dow)
                            avatar = None
                            message = ""
                            continue  # go to next row

                    if avatar_encountered:
                        avatar = text.strip()
                        avatar_encountered = False
                        message = ""
                        continue  # go to next row

                    if avatar is not None \
                            and text not in ["---START---", "---END---"] \
                            and not text.startswith("Patriot Coalition of Oregon removed") \
                            and text.find("hasn't responded. They'll no longer receive messages from this group") < 0:
                        # build up this
                        # avatar's message text
                        message += f"{text} "

                # end-of-file processing
                level_break_on_dts_change(cursor, csv_writer, avatar, message, dts, day, dow)
                cursor.close()
        conn.commit()


if __name__ != "leaked_message_extractor":
    extract_leaked_messages()
