import sqlite3
import os
import logging
from sqlops import *
from utils import is_directory_empty_of_files
import subprocess

def add_content(added: list):

    # TODO: requirements:
    # 0. the content is in assets
    # 1. the content is an article (in a column or in the 'others' folder)
    #   1.1 the article is in a column
    #       1.1.1 the article is readme.md
    #       1.1.2 the article is just a new article
    #   1.2 the article is in the others
    #       1.2.1 the article is readme.md
    #       1.2.2 the article is just a new article
    # 2. the content is a new log
    # 3. the content is a new column
    #   3.1 the content is readme.md
    #   3.2 the content is just a new column
    # 4. the new content path is not legal

    for new_file in added:
    
        path = os.getenv("NOTE_REPO_PATH")
        splitted_path = os.path.split(new_file)
        # case 0 & 4
        if len(splitted_path) < 2:
            logging.warning("File " + new_file + " is placed directly in the root directory. \
                            It will be saved but will be ignored in the database.")
            continue
        elif len(splitted_path) > 2:
            if splitted_path[1] == "assets" and len(splitted_path) == 3:
                continue
            logging.error("The path of " + new_file + " is too deep. \
                           It will be ignored in the database.")
            continue
        dirname, filename = splitted_path

        # case 3 | case 1 & 2
        if find_column(dirname) is None:
            column_id = create_column(dirname)
            if filename.lower() == "readme.md":
                fill_column(column_id, new_file)
            else:
                add_article(column_id, new_file)
        else:
            # case 2 | case 1
            if dirname == "logs":
                add_log(new_file)
            else:
                column_id = find_column(dirname)
                # case 1: combine 1.1 and 1.2, 'others' are treated as a column
                if filename.lower() == "readme.md":
                    fill_column(column_id, new_file)
                else:
                    add_article(column_id, new_file)


def modify_content(modified: list):

    # TODO: requirements:
    # 1. the file is in assets
    # 2. the file is an article (in a column or in the 'others')
    #   2.1 the file is readme.md (need to change the abstract of the column)
    #   2.2 the file is just a modified article
    # 3. the file is a log
    # 4. the file is not legal

    for changed_file in modified:

        path = os.getenv("NOTE_REPO_PATH")
        splitted_path = os.path.split(new_file)
        # case 1 & 4
        if len(splitted_path) < 2:
            logging.warning("File " + new_file + " is placed directly in the root directory. \
                            It will be saved but will be ignored in database modification.")
            continue
        elif len(splitted_path) > 2:
            if splitted_path[1] == "assets" and len(splitted_path) == 3:
                continue
            logging.error("The path of " + new_file + " is too deep. \
                           It will be ignored in database modification.")
            continue
        dirname, filename = splitted_path

        # case 3 | case 2
        if dirname == "logs":
            update_log(changed_file)
        else:
            if filename.lower() == "readme.md":
                column_id = find_column(dirname)
                update_column(column_id, changed_file)
            else:
                update_article(changed_file)

def remove_content(removed: list):

    # TODO: requirements:
    # 1. the file is in assets
    # 2. the file is in a column
    #   2.1 deletion of the file cause the column to be empty (even readme is deleted)
    #   2.2 after deletion, the column is not empty
    # 3. the file is in the 'others'
    # 3. the file is a log
    # 4. the file is not legal

    for removed_file in removed:

        path = os.getenv("NOTE_REPO_PATH")
        splitted_path = os.path.split(removed_file)
        # case 1 & 4
        if len(splitted_path) < 2:
            logging.warning("File " + new_file + " is placed directly in the root directory. \
                            this remove will be ignored in database modification.")
            continue
        elif len(splitted_path) > 2:
            if splitted_path[1] == "assets" and len(splitted_path) == 3:
                continue
            # actually impossible to reach here
            logging.error("The path of " + new_file + " is too deep. \
                           It will be ignored in database modification.")
            continue
        dirname, filename = splitted_path

        # case 3 | case 2
        if dirname == "logs":
            remove_log(removed_file)
        else:
            if dirname == "others":
                remove_article(removed_file)
            else:
                dirpath = os.path.join(os.getenv("NOTE_REPO_PATH"), dirname)
                # case 2.1 | case 2.2
                if is_directory_empty_of_files(dirpath):
                    remove_article(removed_file)
                    remove_column(dirname)
                else:
                    remove_article(removed_file)
 
    


if __name__ == '__main__':
    add_content(["hello/hello.txt", "hello"])
