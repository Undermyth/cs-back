import os
import logging
from sqlops import *
from utils import is_directory_empty_of_files

def add_content(added: list, logger):

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
        splitted_path = new_file.split('/')
        # case 0 & 4
        if len(splitted_path) < 2:
            logger.info("File " + new_file + " is placed directly in the root directory. \
                            It will be saved but will be ignored in the database.")
            continue
        elif len(splitted_path) > 2:
            if splitted_path[1] == "assets" and len(splitted_path) == 3:
                continue
            logger.info("The path of " + new_file + " is too deep. \
                           It will be ignored in the database.")
            continue
        # do not deal with hidden files (like .git, .obsidian)
        if splitted_path[0][0] == ".":
            logger.info(f"The file {new_file} is in a hidden directory. Skipped.")
            continue
        dirname, filename = splitted_path

        logger.info(f"addition of {new_file} is to be read into database.")
        # case 3 | case 1 & 2
        if dirname != "logs" and find_column(dirname) is None:
            logger.info(f"creating new column with the path {dirname}")
            column_id = create_column(dirname)
            logger.info(f"new column {dirname} is given id {column_id}")
            if filename.lower() == "readme.md":
                fill_column(column_id, new_file, logger)
            else:
                add_article(column_id, new_file, logger)
        else:
            # case 2 | case 1
            if dirname == "logs":
                add_log(new_file)
            else:
                column_id = find_column(dirname)
                # case 1: combine 1.1 and 1.2, 'others' are treated as a column
                if filename.lower() == "readme.md":
                    fill_column(column_id, new_file, logger)
                else:
                    add_article(column_id, new_file, logger)


def modify_content(modified: list, logger):

    # TODO: requirements:
    # 1. the file is in assets
    # 2. the file is an article (in a column or in the 'others')
    #   2.1 the file is readme.md (need to change the abstract of the column)
    #   2.2 the file is just a modified article
    # 3. the file is a log
    # 4. the file is not legal

    for changed_file in modified:

        path = os.getenv("NOTE_REPO_PATH")
        splitted_path = changed_file.split('/')
        # case 1 & 4
        if len(splitted_path) < 2:
            logging.warning("File " + changed_file + " is placed directly in the root directory. \
                            It will be saved but will be ignored in database modification.")
            continue
        elif len(splitted_path) > 2:
            if splitted_path[1] == "assets" and len(splitted_path) == 3:
                continue
            logging.error("The path of " + changed_file + " is too deep. \
                           It will be ignored in database modification.")
            continue
        # do not deal with hidden files (like .git, .obsidian)
        if splitted_path[0][0] == ".":
            logger.info(f"The file {changed_file} is in a hidden directory. Skipped.")
            continue
        dirname, filename = splitted_path

        logger.info(f"modification of {changed_file} is to be read into database.")
        # case 3 | case 2
        if dirname == "logs":
            update_log(changed_file)
        else:
            if filename.lower() == "readme.md":
                column_id = find_column(dirname)
                update_column(column_id, changed_file)
            else:
                update_article(changed_file)

def remove_content(removed: list, logger):

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
        splitted_path = removed_file.split('/')
        # case 1 & 4
        if len(splitted_path) < 2:
            logger.warning("File " + removed_file + " is placed directly in the root directory. \
                            this remove will be ignored in database modification.")
            continue
        elif len(splitted_path) > 2:
            if splitted_path[1] == "assets" and len(splitted_path) == 3:
                continue
            # actually impossible to reach here
            logger.error("The path of " + removed_file + " is too deep. \
                           It will be ignored in database modification.")
            continue
        # do not deal with hidden files (like .git, .obsidian)
        if splitted_path[0][0] == ".":
            logger.info(f"The file {removed_file} is in a hidden directory. Skipped.")
            continue
        dirname, filename = splitted_path

        logger.info(f"removal of file {removed_file} is to be read into database.")
        # case 3 | case 2
        if dirname == "logs":
            remove_log(removed_file)
        else:
            if dirname == "others":
                remove_article(removed_file)
            else:
                dirpath = os.path.join(os.getenv("NOTE_REPO_PATH"), dirname)
                # case 2.1 | case 2.2
                if not os.path.exists(dirpath) or is_directory_empty_of_files(dirpath):
                    remove_article(removed_file)
                    logger.info(f"the column {dirpath} is empty. removing the column from database")
                    remove_column(dirname, logger)
                else:
                    remove_article(removed_file)
 
    


if __name__ == '__main__':
    add_content(["hello/hello.txt", "hello"])
