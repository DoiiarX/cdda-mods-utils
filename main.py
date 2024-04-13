# -*- coding: utf-8 -*-
"""
此模块提供功能以计算文件夹大小，将JSON数据转换为定制的YAML格式，以及创建压缩文件。

主要功能包括：
- 计算指定文件夹的总大小。
- 将特定JSON文件转换为定制的YAML格式，主要用于配置文件的生成。
- 压缩指定文件夹为ZIP文件。
"""

import json
import yaml
import os
import shutil
from collections import OrderedDict

def calculate_folder_size(folder_path):
    """
    计算指定文件夹的总大小。

    参数:
    - folder_path: 字符串，表示文件夹的路径。

    返回:
    - total_size: 整数，文件夹的总大小，以字节为单位。
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size

def convert_json_to_custom_yaml(json_file_path, dirname):
    """
    将JSON文件内容转换为定制的YAML格式。

    参数:
    - json_file_path: 字符串，JSON文件的路径。
    - dirname: 字符串，包含JSON文件的目录名称，用于构建下载链接。

    返回:
    - yaml_contents: 字符串，转换后的YAML内容。
    """
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    yaml_contents = ""

    if isinstance(json_data, list):
        for item in json_data:
            # 处理字典类型的name字段
            name = item.get("name", "")
            if not name:
                continue
            type = item.get("type", "")
            if type != 'MOD_INFO':
                continue
            if isinstance(name, dict):
                name = " | ".join([f"{k}: {v}" for k, v in name.items()])

            id_value = item.get("id", item.get("ident", "unknown"))
            if isinstance(id_value, str):
                id_value = f'{id_value}'
            elif isinstance(id_value, list):
                id_value = ''.join([f'    - {id}\n' for id in id_value])
                
            authors = item.get("authors", "unknown")
            if isinstance(authors, str):
                authors = [f'{authors}']
                authors = ''.join([f'    - "{author}"\n' for author in authors])
            elif isinstance(authors, list):
                authors = ''.join([f'    - "{author}"\n' for author in authors])
                
            maintainers = item.get("maintainers", "unknown")
            if isinstance(maintainers, str):
                maintainers = [f'{maintainers}']
                maintainers = ''.join([f'    - {maintainer}\n' for maintainer in maintainers])
            elif isinstance(maintainers, list):
                maintainers = ''.join([f'    - {maintainer}\n' for maintainer in maintainers])
            
            # 处理多行description字段
            description = item.get("description", "No description provided.")
            formatted_description = ""
            if isinstance(description, str):
                formatted_description = "\n    ".join(description.splitlines())
            elif isinstance(description, list):
                formatted_description = "\n    ".join(description)
            elif isinstance(description, dict):
                formatted_description = "\n    ".join([f"{k}: {v}" for k, v in description.items()])

            # 构造homepage字段的URL
            download_url = f"https://alist.doiiars.com/d/Public/Cataclysmdda/{dirname}.zip"
            
            folder_size = calculate_folder_size(dirname)
            
            yaml_contents = "- type: direct_download\n" 
            yaml_contents += '  ident: "' + id_value + '"\n' 
            yaml_contents += '  name: "' + name + '"\n' 
            yaml_contents += "  authors: \n" + authors
            yaml_contents += '  maintainers: \n' + maintainers
            yaml_contents += "  description: |\n    " + formatted_description + "\n" 
            yaml_contents += "  category: '" + item.get("category", "unknown") + "'\n" 
            yaml_contents += "  dependencies:\n" + ''.join([f"    - '{dependency}'\n" for dependency in item.get("dependencies", [])]) 
            yaml_contents += f"  size: {folder_size}\n" 
            yaml_contents += '  url: "' + download_url + '"\n' 
            yaml_contents += "  homepage: 'https://github.com/Kenan2000/CDDA-Structured-Kenan-Modpack'"

        return yaml_contents
    else:
        print(f"文件 {json_file_path} 的格式不正确。期望的是一个列表。")
        return ""




def find_folders_and_convert_json():
    """
    查找当前目录下的所有文件夹，并尝试转换包含的modinfo.json文件。
    """
    current_directory = os.getcwd()
    folders = [f for f in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, f))]

    all_yaml_content = ''

    for folder in folders:
        json_file_path = os.path.join(current_directory, folder, 'modinfo.json')

        if os.path.exists(json_file_path):
            yaml_content = convert_json_to_custom_yaml(json_file_path, folder)
            if yaml_content:
                all_yaml_content += yaml_content + '\n\n'

    if all_yaml_content:
        yaml_file_path = os.path.join(current_directory, 'all_modinfo.yaml')
        with open(yaml_file_path, 'a', encoding='utf-8') as yaml_file:
            yaml_file.write(all_yaml_content)
        print(f'所有YAML内容已追加到 {yaml_file_path}')
    else:
        print('没有找到任何modinfo.json文件来转换。')


def create_zip_files():
    """
    压缩当前目录下的每个文件夹为ZIP文件。
    """
    current_directory = os.getcwd()
    folders = [f for f in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, f))]

    for folder in folders:
        folder_path = os.path.join(current_directory, folder)
        zip_file_name = folder

        # Create a zip file with the folder's name
        shutil.make_archive(zip_file_name, 'zip', folder_path)

        print(f'Folder "{folder}" has been zipped as "{zip_file_name}".')
        
if __name__ == "__main__":
    find_folders_and_convert_json()
    # create_zip_files()