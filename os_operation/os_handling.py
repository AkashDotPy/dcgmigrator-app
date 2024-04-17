import os
import shutil
import multiprocessing
import platform
from dcgmigrator_core.logging_operation import HandleLogging

# log_instance = HandleLogging()
# logger = log_instance.handle_log()

class DirectoryPath:
    def __init__(self, project_name):
        self.project_name = project_name
        self.log_instance = HandleLogging(self.project_name)
        self.logger = self.log_instance.handle_log()

    def report_path(self):
        parent_directory = os.getcwd()
        output_directory = r"report_folder"
        path = os.path.join(parent_directory,output_directory)
        try:
            os.makedirs(path, exist_ok = True)
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{output_directory}")
        return path
    
    # def dcg_report_path(self,project_name):
    #     parent_directory = rf"report_{project_name}"
    #     output_directory = r"dcgmigrator_report"
    #     path = os.path.join(parent_directory,output_directory)
    #     try:
    #         os.makedirs(path, exist_ok = True)
    #     except OSError as e:
    #         self.logger.error(f"Error :{e} \n Invalid directory{output_directory}")
    #     return path
    
    def sqlite_database_path(self):
        db_folder = "database"
        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, "dcgmigrator.db")
        return db_path
    
    def convert_output_dir(self,project_name):
        parent_directory = r"Converted_files"
        output_directory = fr"{project_name}"
        dir_path = os.path.join(parent_directory,output_directory)
        try:
            os.makedirs(dir_path, exist_ok = True)
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{output_directory}")
        return dir_path
    
    def config_path(self,project_name):
        parent_directory = r"temp"
        output_file = fr"{project_name}_ora2pg.conf"
        dir_path = os.path.join(parent_directory,output_file)
        try:
            os.makedirs(os.path.dirname(dir_path), exist_ok=True)
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{dir_path}")
        return dir_path,parent_directory
    
    def remove_config_files(self,project_name):
        path, parent_directory = self.config_path(project_name)
        try:
            if os.path.exists(path):
                os.remove(path)
            else:
                self.logger.error(f"File does not '{path}' does not exist.")
            
        except Exception as e:
            self.logger.error(f"Directory or file cannot be removed\n{e}")


    def files_in_output(self,dir_path):
        dir_files = os.listdir(dir_path)
        return dir_files
       
    def cpu_core(self,file_name):
        os_name = platform.system()
        count = multiprocessing.cpu_count() 
        
        if os_name != "Windows":
            core_count = int(count / 2)
            return core_count
        else:
            self.logger.error(f"unable to deploy : {file_name}\nora2pg load does not support windows")
            

    def trigger_report_path(self,pg_schema):
        parent_directory = r"report_folder"
        output_directory = fr"trigger_sanity_{pg_schema}"
        path = os.path.join(parent_directory,output_directory)
        try:
            os.makedirs(path, exist_ok = True)
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{output_directory}")
        return path
    
    def code_report_path(self,pg_schema):
        parent_directory = r"report_folder"
        output_directory = fr"code_sanity_{pg_schema}"
        path = os.path.join(parent_directory,output_directory)
        try:
            os.makedirs(path, exist_ok = True)
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{output_directory}")
        return path
    
    def ora_home(self):
        oracle_home = os.environ.get('ORACLE_HOME')
        # oracle_home = ""
        return oracle_home
    
    def project_env(self):
        project_name = os.environ.get('PROJECT_NAME')
        print(project_name)
        return project_name
    
    def log_dir(self):
        parent_directory = r""
        output_directory = fr"logs"
        path = os.path.join(parent_directory,output_directory)
        try:
            os.makedirs(path, exist_ok = True)
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{output_directory}")
        return path
    
    def os_join(self,dir_path,file):
        file_path = os.path.join(dir_path,file)
        return file_path
    
    def dcg_report_path(self,project_name,file_name,output_dir=None):
        try:
            report_path = os.environ.get('DCG_REPORT_PATH')
            parent_dir = rf"report_{project_name}"
            dcg_dir = r"dcgmigrator_report"
            if report_path and os.path.exists(report_path):
                path = os.path.join(report_path,parent_dir,dcg_dir,output_dir)
            else:
                path = os.path.join(parent_dir,dcg_dir,output_dir)
            os.makedirs(path, exist_ok = True)
            file_path = os.path.join(path,file_name)
            return file_path
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{path}")
        
    def ora2pg_test_report(self,project_name):
        try:
            report_path = os.environ.get('DCG_REPORT_PATH')
            parent_dir = rf"report_{project_name}"
            ora_dir = r"ora2pg_report"
            if report_path and os.path.exists(report_path):
                path = os.path.join(report_path,parent_dir,ora_dir)
            else:
                path = os.path.join(parent_dir,ora_dir)
            os.makedirs(path, exist_ok = True)
            return path
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{ora_dir}")
        
    def _code_conv_report(self,project_name,output_dir,type,file_name):
        try:
            report_path = os.environ.get('DCG_REPORT_PATH')
            parent_dir = rf"report_{project_name}"
            dcg_dir = r"dcgmigrator_report"
            if report_path and os.path.exists(report_path):
                path = os.path.join(report_path,parent_dir,dcg_dir,output_dir,type)
            else:
                path = os.path.join(parent_dir,dcg_dir,output_dir,type)

            os.makedirs(path, exist_ok = True)
            file_path = os.path.join(path,file_name)
            return file_path
        except OSError as e:
            self.logger.error(f"Error :{e} \n Invalid directory{path}")


    
    def code_sanity_report_path(self,project_name,file_name,schema):
        return self.dcg_report_path(project_name,file_name,f"code_sanity_{schema}")
    
    def trigger_sanity_report_path(self,project_name,file_name,schema, runtype ="POST_DATALOAD"):
        if runtype == "POST_DATALOAD":
            return self.dcg_report_path(project_name,file_name,f"trigger_sanity_{schema}")
        else:
            return self.dcg_report_path(project_name,file_name,f"trigger_sanity_{runtype}_{schema}")

    def ora_assessment_report_path(self,project_name,file_name):
        return self.dcg_report_path(project_name,file_name,"Oracle_assessment_report")
    
    def schema_Validation_report_path(self,project_name,file_name,ora_name):
        return self.dcg_report_path(project_name,file_name,f"dcg_schema_validation_{ora_name}")
    
    def dcg_ora_validation_report_path(self,project_name,file_name):
        return self.dcg_report_path(project_name,file_name,f"dcg_ora2pg_validation")
    
    # def count_validation_report_path(self,project_name,file_name,ora_name):
    #     return self.dcg_report_path(project_name,file_name,f"dcg_count_validation_{ora_name}")
    
    def code_conv_report_img_path(self,project_name,file_name):
        return self._code_conv_report(project_name,"code_conversion_planning_report","images",file_name)
        # return self.dcg_report_path(project_name,file_name,"code_conversion_planning_report")
    
    def code_conv_report_html_path(self,project_name,file_name):
        return self._code_conv_report(project_name,"code_conversion_planning_report","html",file_name)

    def remove_project_dir(self,project_name):
        conv_path = self.convert_output_dir(project_name)
        conv_path_exist = os.path.exists(conv_path)

        report_path = rf"report_{project_name}"
        report_path_exist = os.path.exists(report_path)

        if conv_path_exist  and report_path_exist == True:
            shutil.rmtree(conv_path)
            shutil.rmtree(report_path)
            self.logger.info(f"removed dir {conv_path,report_path} successfully")
            return True
        elif conv_path_exist  and report_path_exist == False:
            self.logger.error(f"Reports directory/file does not exist")
            return False
        
    def ora2pg_error_log(self,project_name):
        directory = os.getcwd()
        output_filename = f"{project_name}_ora2pg_error.log"
        output_dir_path = "logs"
        output_path = self.os_join(output_dir_path,output_filename)
        ora2pg_error = ""
        for filename in os.listdir(directory):
            if filename.endswith("_error.log"):
                file_path = os.path.join(directory, filename)
                exists = os.path.exists(file_path)

                if exists:
                    with open(file_path, "r") as file:
                        file_data = file.read()
                        ora2pg_error += file_data
                    try:
                        os.remove(file_path) 
                        self.logger.info(f"{file_path} is moved to - {output_filename} - data error logs file") 
                    except Exception as e:
                        self.logger.error(f"Unable to move {filename} ora2pg error log file\n{e}")
                try:
                    with open(output_path, "w") as output:
                        output.write(ora2pg_error)
                except Exception as e:
                    self.logger.error(f"{e}\nIssue occured in moving Ora2pg data error file ")
        return True
        
    
    def report_zip_file(self,project_name):
        report_path = os.environ.get('DCG_REPORT_PATH')
        dir_path = f"report_{project_name}"
    
        if report_path and os.path.exists(report_path):
            path = os.path.join(report_path,dir_path)
            shutil.make_archive(path, 'zip', path)
            self.logger.info(f"DCGMigrator zip file is created succsessfully\nReport : {path}")  
        else:
            shutil.make_archive(dir_path, 'zip', dir_path)
            self.logger.info(f"DCGMigrator Zip file created succsessfully\nReport : {dir_path}")
            



        



    
    



                         


    
 