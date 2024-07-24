import shutil
import os

def copy_contents(source_dir, destination_dir):
    for item in os.listdir(source_dir):
        print(item)
        source_path = os.path.join(source_dir, item)
        destination_path = os.path.join(destination_dir, item)
        
        if os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)

source_directory = "dcgmigrator"
destination_directory = os.getcwd()
copy_contents(source_directory, destination_directory)
