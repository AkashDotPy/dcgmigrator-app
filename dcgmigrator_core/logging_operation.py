import logging
import os

class HandleLogging:
    def __init__(self, project_name):
        self.project_name = project_name
        self.logger = logging.getLogger(self.project_name)
        path = self.log_dir()

        if not self.logger.handlers:
            file_name = f"{self.project_name}_logfile.log"
            file_path = os.path.join(path,file_name)

            self.logger.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(file_path, mode="a")  
            file_handler.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO) 

            file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            console_formatter = logging.Formatter("%(levelname)s - %(message)s")

            file_handler.setFormatter(file_formatter)
            console_handler.setFormatter(console_formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def handle_log(self):
        return self.logger
    
    def log_dir(self):
        parent_directory = r""
        output_directory = fr"logs"
        path = os.path.join(parent_directory,output_directory)
        try:
            os.makedirs(path, exist_ok = True)
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{output_directory}")
        return path
