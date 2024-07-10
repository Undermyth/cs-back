import os

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
