import os 
import glob
import json
import asyncio
from datetime import datetime
import time

import xmltodict
import aiofiles
import time

config_path = {}


def move_files(source, destination):
    os.replace(source, destination)

async def write_json_file(data, file_name):
    async with aiofiles.open(file_name, "w") as new_json:
        await new_json.write(json.dumps(data, indent = 4))
    

def create_dir_if_doesnt_exist(path):
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
            move_files(source=file, destination= config_path['old_xml_path'] + cur_file_name)



async def read_path(config_path):

    if config_path['input_xml_file_path']:
        xml_file_path = config_path['input_xml_file_path']
        if os.path.exists(path=xml_file_path):
            await read_all_xmls(xml_file_path, config_path) 
        else:
            raise Exception("configured path doesn't exist")
    else:
        raise Exception("config.path doesn't exist")
    

async def load_config_file():
    with open('config.json', 'r') as cj:
            return json.load(cj)
    
async def main():
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