from email import message
import os 
import glob
import json
import asyncio
from datetime import datetime
import time
import shutil

import xmltodict
import aiofiles
import time

config_path = {}

def get_file_name(config_path):
    print('*****  get_file_name  ******')
    #datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    filename = datetime.utcnow()
    create_dir_if_doesnt_exist(config_path['log_file_path'])
    files = glob.glob(config_path['log_file_path'] + '*.txt', recursive=True)
    print('files',files)
    max_file = None
    if files:
        max_path = max(files, key=os.path.getctime)
        max_file = max_path.split('/')
        print('max_file', max_file)
        interval_time = datetime.strptime(max_file[-1], "%Y%m%dT%H%M%S.txt") - datetime.utcnow()
        
        return max_path
    print('2', config_path['log_file_path'] + datetime.utcnow().strftime("%Y%m%dT%H%M%S.txt"))
    return config_path['log_file_path'] + datetime.utcnow().strftime("%Y%m%dT%H%M%S.txt")
    

async def write_log(message, config_path):
    print('in write log')
    path = get_file_name(config_path=config_path)
    print('path', path)
    async with aiofiles.open(path, "ab+") as new_log:
        print('write log file ')
        await new_log.write(bytes(message, 'utf-8'))
        await new_log.write(bytes('\n', 'utf-8'))
    

def log_message(source, destination, archive_path, config_path):
    a =  config_path['log_message']['from'] + ' : '\
                + source + '\n'\
                + config_path['log_message']['to'] +' : ' \
                + destination + '\n'\
                + config_path['log_message']['archive']+ " : " \
                + archive_path+ '\n'\
                + "================================================================="
    print('a', a)
    return a



def move_files(source, destination, archive_path):
    shutil.copyfile( source,archive_path)
    os.replace(source, destination)
    

async def write_json_file(data, file_name):
    print("** write json ***")
    async with aiofiles.open(file_name, "w") as new_json:
        await new_json.write(json.dumps(data, indent = 4))
    

def create_dir_if_doesnt_exist(path):
    print("** create path ***")
    if not os.path.exists(path):
                os.mkdir(path)

async def read_all_xmls(xml_file_path, config_path):

    print('in read all xmls')
    for file in glob.glob(xml_file_path + "*.xml", recursive=True):
        async with aiofiles.open(file, 'r') as xml_file:
            data = xmltodict.parse(await xml_file.read())
            cur_file_name = file.split('/')[-1]
            create_dir_if_doesnt_exist(config_path['output_json_file_path'])
            
            file_name = cur_file_name[:-4] + str(datetime.utcnow()) + '.json'
            output_file = config_path['output_json_file_path'] + file_name
            await write_json_file(data=data, file_name=output_file)
            
            create_dir_if_doesnt_exist(config_path['old_xml_path'])
            destination = config_path['old_xml_path'] + cur_file_name

            create_dir_if_doesnt_exist(config_path['xml_archive_path'])
            archive_path = config_path['xml_archive_path'] + cur_file_name
            print("move ")
            move_files(
                source=file, 
                destination=destination,
                archive_path=archive_path
            )
            print("log msg")
            message = log_message(
                source=file,
                destination=destination,
                archive_path=archive_path,
                config_path=config_path
            )
            print("file name")
            log_file = get_file_name(config_path=config_path)
            print("write log")
            await write_log(message=message, config_path=config_path)



async def read_path(config_path):
    print("** open read path ***")
    if config_path['input_xml_file_path']:
        xml_file_path = config_path['input_xml_file_path']
        if os.path.exists(path=xml_file_path):
            await read_all_xmls(xml_file_path, config_path) 
        else:
            raise Exception("configured path doesn't exist")
    else:
        raise Exception("config.path doesn't exist")
    

async def load_config_file():
    print("** open config file ***")
    with open('config.json', 'r') as cj:
            return json.load(cj)
    
async def main():
    print('main')
    try:
        config_path = await load_config_file()
        await read_path(config_path)

    except Exception as e:
        print("******* exception ***********")
        print(e)


if __name__ == "__main__":
    till = int(input("Please enter total runtime in mins ")) * 60
    count = 0
    while count < till:
        print('******* processing file **********')
        asyncio.run(main())
        print('****** sleep ********')
        time.sleep(1)
        count += 1