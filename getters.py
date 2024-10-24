import sqlite3
import os
from utils import contains_string_in_file, add_prefix_to_image_links

def article_counts() -> int:
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select count(*) from articles;')
    article_count = next(cursor)[0]
    return article_count

def column_counts() -> int:
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select count(*) from columns;')
    column_count = next(cursor)[0]
    return column_count - 1     # minus 1 for others

def log_counts() -> int:
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select count(*) from logs;')
    log_count = next(cursor)[0]
    return log_count

def logs() -> list:
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id,title,starttime,endtime,len,abstract from logs;')
    results = []
    for row in cursor:
        data = {
            "id": row[0],
            "title": row[1],
            "start_date": row[2],
            "update_date": row[3],
            "length": row[4],
            "abstract": row[5]
        }
        results.append(data)
    conn.close()
    return results

def filtered_logs(filter: str) -> list:
    log_list = logs()
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    filter_result = []
    for item in log_list:
        cursor = conn.execute('select filepath from logs where id = ?;', (item["id"],))
        filepath = next(cursor)[0]
        file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
        filter_result.append(contains_string_in_file(file, filter))
    return [log for log, filtered in zip(log_list, filter_result) if filtered]
        

def articles() -> list:
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id,title,uptime,len,abstract from articles;')
    results = []
    for row in cursor:
        data = {
            "id": row[0],
            "title": row[1],
            "date": row[2],
            "length": row[3],
            "abstract": row[4] + "..."
        }
        results.append(data)
    conn.close()
    return results

def articles_in_column(column_id: str) -> list:
    column_id = int(column_id)
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id,title,uptime,len,abstract from articles where columnid = ?;', (column_id,))
    results = []
    for row in cursor:
        data = {
            "id": row[0],
            "title": row[1],
            "date": row[2],
            "length": row[3],
            "abstract": row[4]
        }
        results.append(data)
    conn.close()
    return results

def filtered_articles(filter: str) -> list:
    article_list = articles()
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    filter_result = []
    for item in article_list:
        cursor = conn.execute('select filepath from articles where id = ?;', (item["id"],))
        filepath = next(cursor)[0]
        file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
        filter_result.append(contains_string_in_file(file, filter))
    return [article for article, filtered in zip(article_list, filter_result) if filtered]

def filtered_column_articles(filter: str, column_id: str) -> list:
    column_id = int(column_id)
    article_list = articles_in_column(column_id)
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    filter_result = []
    for item in article_list:
        cursor = conn.execute('select filepath from articles where id = ?;', (item["id"],))
        filepath = next(cursor)[0]
        file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
        filter_result.append(contains_string_in_file(file, filter))
    return [article for article, filtered in zip(article_list, filter_result) if filtered]

def columns() -> list:
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    query = '''
    SELECT c.id, c.title, c.uptime, COUNT(a.id) as length, c.abstract
    FROM columns c
    LEFT JOIN articles a ON c.id = a.columnid
    WHERE c.id != 0
    GROUP BY c.id, c.title, c.uptime, c.abstract
    '''
    cursor = conn.execute(query)
    results = cursor.fetchall()
    data = [
        {
            "id": row[0],
            "title": row[1],
            "date": row[2],
            "length": row[3],
            "abstract": row[4]
        }
        for row in results
    ]
    conn.close()
    return data

def filtered_columns(filter: str) -> list:
    column_list = columns()
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    filter_result = []
    for item in column_list:
        cursor = conn.execute('select dirpath from columns where id = ?;', (item["id"],))
        dirpath = next(cursor)[0]
        file = os.path.join(os.getenv("NOTE_REPO_PATH"), dirpath, "Readme.md")
        filter_result.append(contains_string_in_file(file, filter))
    conn.close()
    return [column for column, filtered in zip(column_list, filter_result) if filtered]

def single_article(article_id: str):
    article_id = int(article_id)
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select filepath,title,uptime,len from articles where id = ?;', (article_id,))
    article = next(cursor)
    file = os.path.join(os.getenv("NOTE_REPO_PATH"), article[0])
    with open(file, 'r') as f:
        content = f.read()

    splitted_path = article[0].split('/')
    dirpath = splitted_path[0]
    prefix = f"http://121.40.91.43:5000/images/{dirpath}/assets/"
    content = add_prefix_to_image_links(content, prefix)

    return {
        "content": content,
        "title": article[1],
        "time": article[2],
        "length": article[3],
    }

def single_log(log_id: str):
    log_id = int(log_id)
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select filepath,title,endtime,len from logs where id = ?;', (log_id,))
    log = next(cursor)
    file = os.path.join(os.getenv("NOTE_REPO_PATH"), log[0])
    with open(file, 'r') as f:
        content = f.read()

    prefix = f"http://121.40.91.43:5000/images/logs/assets/"
    content = add_prefix_to_image_links(content, prefix)

    return {
        "content": content,
        "title": log[1],
        "endtime": log[2],
        "len": log[3],
    }

def single_column(column_id: str):
    column_id = int(column_id)
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    query = '''
    SELECT c.id, c.title, c.uptime, COUNT(a.id) as length, c.abstract
    FROM columns c
    LEFT JOIN articles a ON c.id = a.columnid
    WHERE c.id == ?
    GROUP BY c.id, c.title, c.uptime, c.abstract
    '''
    cursor = conn.execute(query, (column_id,))
    result = next(cursor)
    conn.close()
    return {
        "title": result[1],
        "time": result[2],
        "length": result[3],
        "abstract": result[4]
    }
    


