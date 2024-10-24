import os
from termcolor import colored
import logging
import sys
import argparse
import hashlib
import hmac
import re

def is_directory_empty_of_files(directory):
    # 遍历目录的内容
    for entry in os.listdir(directory):
        # 获取完整路径
        full_path = os.path.join(directory, entry)
        
        # 如果找到的是文件，立即返回 False
        if os.path.isfile(full_path):
            return False
            
    # 如果没有找到任何文件，返回 True
    return True

def contains_string_in_file(file_path, search_string):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if search_string in line:
                    return True
        return False
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return False

def add_prefix_to_image_links(content, prefix):
    # 定义正则表达式匹配 Markdown 图片链接
    pattern = r'!\[(.*?)\]\((.*?)\)'
    
    # 使用替换函数给图片链接添加前缀
    def replace_with_prefix(match):
        alt_text = match.group(1)
        image_url = match.group(2)
        new_url = f"{prefix}{image_url}"
        return f'![{alt_text}]({new_url})'
    
    # 使用 sub 函数替换所有匹配项
    modified_content = re.sub(pattern, replace_with_prefix, content)
    
    return modified_content

def create_logger():
    # create a logger
    logger = logging.getLogger("BackEndLogger")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # create formatter
    fmt = '[%(asctime)s %(name)s] (%(filename)s %(lineno)d): %(levelname)s %(message)s'
    color_fmt = colored('[%(asctime)s %(name)s]', 'green') + \
                colored('(%(filename)s %(lineno)d)', 'yellow') + ': %(levelname)s %(message)s'

    # create console handlers for master process
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter(fmt=color_fmt, datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(console_handler)

    # create file handlers
    file_handler = logging.FileHandler('backend.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(file_handler)

    return logger

def route_exist(path):
    '''
    verify if the path (like 'others/blog.md') exists in the backend repo
    '''
    root_path = os.getenv("NOTE_REPO_PATH")
    full_path = os.path.join(root_path, path)
    return os.path.exists(full_path)


def parse_arguments(logger):
    parser = argparse.ArgumentParser(description='Process command line arguments.')

    parser.add_argument('--temp', action='store_true', help='Operate database in a manual way')

    temp_args = parser.add_argument_group('Manual mode arguments')
    temp_args.add_argument('--add', type=str, nargs='?', const='', 
                           help='Add files.\nYou can offer a list of path here (like others/blog.md).\n\
                            Note that manual operations should be done after the note repo is pulled.\n\
                            i.e. for add operation, the file should exist in the repo already.')
    temp_args.add_argument('--modify', type=str, nargs='?', const='', 
                           help='Modify files.\nFor modify operation, the file should exist in the repo\
                            already.')
    temp_args.add_argument('--remove', type=str, nargs='?', const='', 
                           help='Remove files.\nFor remove operation, the file should NOT exist in the \
                            current repo.')

    args = parser.parse_args()

    if args.temp:
        res = process_temp_mode(args, logger)
    else:
        res = None
        if any([args.add, args.modify, args.remove]):
            raise ValueError("Cannot manually operate the database in normal mode. Please specify --temp.")
        logger.info("Boosting backend as a normal service.")

    return args.temp, res

def split_file_list(file_string):
    return [f.strip() for f in file_string.split(',') if f.strip()]

def process_temp_mode(args, logger):
    if not any([args.add, args.modify, args.remove]):
        raise ValueError("At least one of --add, --modify, or --remove must be provided when using --temp.")
    
    add_files = split_file_list(args.add) if args.add else []
    modify_files = split_file_list(args.modify) if args.modify else []
    remove_files = split_file_list(args.remove) if args.remove else []

    for file in add_files:
        if not route_exist(file):
            raise ValueError(f"The file {file} is required to be added to database, but it is not in the note repo.")
    
    for file in modify_files:
        if not route_exist(file):
            raise ValueError(f"The file {file} is required to be added to database, but it is not in the note repo.")
    
    for file in remove_files:
        if route_exist(file):
            raise ValueError(f"The file {file} is required to be removed from database, but it is still in the note repo.")

    logger.info(f"Adding files: {add_files}")
    logger.info(f"Modifying files: {modify_files}")
    logger.info(f"Removing files: {remove_files}")

    return add_files, modify_files, remove_files

def get_secret():
    with open("SECRET") as f:
        secret = f.read()
    return secret

'''modified from https://docs.github.com/zh/webhooks/using-webhooks/validating-webhook-deliveries#examples'''
def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha1)
    expected_signature = "sha1=" + hash_object.hexdigest()
    print(expected_signature, signature_header)
    if not hmac.compare_digest(expected_signature, signature_header):
        return False
    return True
