import sqlite3
import os
import datetime
from dotenv import load_dotenv
import markdown
from bs4 import BeautifulSoup

def create_column(dirpath: str) -> int:

    # current date is served as the 'uptime'
    # title and abstract of the column should be read from README.md
    # create an id for new column
    
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select max(id) from columns;')
    max_id = next(cursor)[0]
    if max_id is None:
        max_id = -1
    new_id = max_id + 1

    cursor = conn.cursor()
    cursor.execute('insert into columns(id, uptime, dirpath)\
                   values (?, DATE(\'now\'), ?);', 
                   (new_id, dirpath))
    conn.commit()
    conn.close()

def fill_column(column_id: int, filepath: str):
    """fill the column information with readme.md

    Args:
        column_id (int): the id of the column
        filepath (str): "column/readme.md", "column/README.md" or other forms of the readme file
    """
    # TODO: not tested

    file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
    with open(file) as f:
        text = f.read()
        text = markdown.markdown(text)
        soup = BeautifulSoup(text, 'lxml')
        title = soup.h1.string
        abstract = soup.p.string

    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.cursor()
    cursor.execute('update columns set title = ?, abstract = ? \
                   where id = ?;', (title, abstract, column_id))
    conn.commit()
    conn.close()

def find_column(dirpath: str) -> int:

    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id from columns where dirpath = ?;', (dirpath,))
    id = next(cursor)[0]
    conn.close()
    return id

def generate_id():
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d')
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id from articles;')
    max_id = int(date) * 100
    for row in cursor:
        if row[0] // 100 == int(date) and row[0] > max_id:
            max_id = row[0]
    max_id = max_id + 1
    print(max_id)

def add_article(column_id: int, filepath: str):
    """add an article to an existing column

    Args:
        column_id (int): id of the column to be add
        filepath (str): "<column_name>/<filename>"
    """    
    new_id = generate_id()

    # get title and abstract from README.md
    file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        length = len(text)
        html_text = markdown.markdown(text)
        title = html_text.h1.string
        lines = f.readlines()
        contents = lines[1:]
        abstract = " ".join(contents).strip()
        if len(abstract) > 50:
            abstract = abstract[:50]
    
    # insert new article
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.cursor()
    cursor.execute('insert into articles \
                   values (?, ?, DATE(\'now\'), ?, ?, ?, ?);', 
                   (new_id, title, filepath, abstract, length, column_id))
    conn.commit()
    conn.close()

def add_log(filepath: str):

    # get title number of logs and abstract from README.md
    file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        html_text = markdown.markdown(text)
        soup = BeautifulSoup(html_text, 'lxml')
        title = soup.h1.string
        abstract = soup.p.string
        num_of_logs = len(soup.find_all('h2'))

    # get a new id
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select max(id) from logs;')
    max_id = next(cursor)[0]
    if max_id is None:
        max_id = -1
    new_id = max_id + 1

    # insert new log
    cursor = conn.cursor()
    cursor.execute('insert into logs \
                   values (?, ?, ?, DATE(\'now\'), DATE(\'now\'), ?, ?);', 
                   (new_id, title, filepath, num_of_logs, abstract))
    conn.commit()
    conn.close()

def update_log(filepath: str):

    # TODO: not tested

    # get the id of the log
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id from logs where filepath = ?', filepath)
    id = next(cursor)[0]

    # get title number of logs and abstract from README.md
    file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        html_text = markdown.markdown(text)
        soup = BeautifulSoup(html_text, 'lxml')
        title = soup.h1.string
        abstract = soup.p.string
        num_of_logs = len(soup.find_all('h2'))

    cursor = conn.cursor()
    cursor.execute('update logs set \
                   title = ?, abstract = ?, endtime = DATE(\'now\'), len = ? where id = ?;', 
                   (title, abstract, num_of_logs, id))
    conn.commit()
    conn.close()

def update_article(filepath: str):

    # TODO: not tested

    # get the id of the article
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id, columnid from articles where filepath = ?', filepath)
    article_id, column_id = next(cursor)

    # get title and abstract from README.md
    file = os.path.join(os.getenv("NOTE_REPO_PATH"), filepath)
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        html_text = markdown.markdown(text)
        title = html_text.h1.string
        lines = f.readlines()
        contents = lines[1:]
        abstract = " ".join(contents).strip()
        if len(abstract) > 50:
            abstract = abstract[:50]

    cursor = conn.cursor()
    cursor.execute('update articles set \
                   title = ?, uptime = DATE(\'now\'), abstract = ?, len = ? where id = ?;', 
                   (title, abstract, len(text), article_id))
    # also update the update time of the column
    cursor.execute('update columns set \
                   uptime = DATE(\'now\') where id = ?;', (column_id,))
    conn.commit()
    conn.close()


def update_column(column_id: int, filepath: str):
    '''
    update the abstract of the column, because the readme is modified
    also modify the updated time
    '''

    # TODO: not tested
    with open(filepath) as f:
        text = f.read()
        text = markdown.markdown(text)
        soup = BeautifulSoup(text, 'lxml')
        title = soup.h1.string
        abstract = soup.p.string
     
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.cursor()
    cursor.execute('update columns set \
                   title = ?, uptime = DATE(\'now\'), abstract = ? where id = ?;', 
                   (title, abstract, column_id))
    conn.commit()
    conn.close()

def remove_log(filepath: str):

    # TODO: not tested

    # get the id of the log
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id from logs where filepath = ?', filepath)
    id = next(cursor)[0]

    cursor = conn.cursor()
    cursor.execute('delete from logs where id = ?;', (id,))
    conn.commit()
    conn.close()

def remove_article(filepath: str):

    # TODO: not tested

    # get the id of the article
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id from articles where filepath = ?', filepath)
    id = next(cursor)[0]

    cursor = conn.cursor()
    cursor.execute('delete from articles where id = ?;', (id,))
    conn.commit()
    conn.close()

def remove_column(dirpath: str):

    # TODO: not tested

    # get the id of the column
    conn = sqlite3.connect(os.path.join(os.getenv("DB_PATH"), "main.db"))
    cursor = conn.execute('select id from columns where dirpath = ?;', (dirpath,))
    id = next(cursor)[0]

    cursor = conn.cursor()
    cursor.execute('delete from columns where id = ?;', (id,))
    conn.commit()
    conn.close()
    

if __name__ == '__main__':
    create_column('hello')
