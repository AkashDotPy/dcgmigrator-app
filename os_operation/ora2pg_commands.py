import os
import subprocess as sp
from dcgmigrator_config.config import ConfigInputs 
from os_operation.os_handling import DirectoryPath
from os_operation.os_platform import OSPlatform
from dcgmigrator_core.logging_operation import HandleLogging
from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_plus.extension_plus import Extention
from database_operation.postgres import PostgresDatabase
import sys
import re


class ora2pgCommand:

    def __init__(self, project_name):
        self.project_name = project_name
        self.platform_inst = OSPlatform(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        self.config_instance = ConfigInputs(self.project_name)
        self.sqlite_inst = SqliteDatabaseManagement(self.project_name)
        self.extension_plus = Extention(self.project_name)
        self.pginst = PostgresDatabase(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()


    def show_version(self,project_name):
        command = fr"ora2pg -v"
        result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT,  shell=True )
        output = result.stdout.decode("utf-8")
        print(output)
        self.logger.debug(f"show_version logs for project - {project_name} - {output}")
        return result
      
    def show_schema(self, project_name):
        path,success =  self.config_instance.refresh_ora2pg_config(project_name)
        if success:
            command = fr"ora2pg -t SHOW_SCHEMA  -c {path} "
            result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT,  shell=True )
            output = result.stdout.decode("utf-8")
            print(output)
            self.logger.debug(f"show_schema logs for project - {project_name} - {output}")
            self.os_inst.remove_config_files(project_name)
            return result
    
    def show_table(self, project_name):
        path,success = self.config_instance.refresh_ora2pg_config(project_name)
        if success:
            command = fr"ora2pg -t SHOW_TABLE  -c {path}" 
            result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT,  shell=True )
            output = result.stdout.decode("utf-8")
            print(output)

            self.logger.debug(f"show_table logs for project - {project_name} - {output}")
            self.os_inst.remove_config_files(project_name)  
            return result

    
    def show_column(self,project_name):
        path,success =  self.config_instance.refresh_ora2pg_config(project_name)
        if success:
            command = fr"ora2pg -t SHOW_COLUMN  -c {path}"
            result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT,  shell=True )
            output = result.stdout.decode("utf-8")
            print(output)
            self.logger.debug(f"show_column logs for project - {project_name} - {output}")
            self.os_inst.remove_config_files(project_name)
            return result

    def convertion(self,project_name, type):
        temp_path,success = self.config_instance.refresh_ora2pg_config(project_name)
        self.os_inst.log_dir()
        output_path = self.os_inst.convert_output_dir(project_name)
        try:
            command = fr"ora2pg -t {type}  -c {temp_path} --basedir {output_path} --out {type}.sql "
            result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT,  shell=True )
            output = result.stdout.decode("utf-8") ;
            self.logger.debug(f"- Msg - {output}")
                    
        except Exception as e:
            self.logger.error(f"Convert command (ora2pg) is unable to execute\n{e}")
            sys.exit(1)

    def copy_data_movement(self,project_name,use_oraclefdw , continue_on_error , data_limit):
        if use_oraclefdw:
            self.extension_plus.oracle_fdw_flag(project_name)
        
        if continue_on_error:
            self.sqlite_inst.insert_ora2pgconfig(project_name,"LOG_ON_ERROR","1")
        else:
             self.sqlite_inst.remove_config(project_name,"LOG_ON_ERROR")

        temp_path,success = self.config_instance.refresh_ora2pg_config(project_name)
        #run only for migrated tables
        tablelist = self.pginst.fetch_table_exists(project_name)
        if not tablelist is None:
            self.logger.info(f"\nData transfer begin for project : {project_name} .......")
            command = fr"ora2pg -t COPY -c {temp_path} -a {tablelist} " + (' -W "ROWNUM < ' + str(data_limit + 1) + '"'  if data_limit is not None else "")
            result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
            
            if result.returncode != 0  and not continue_on_error:
                output = result.stdout.decode("utf-8")
                self.logger.debug(f"Data transfer logs - Project : {project_name} - {output}")
                self.logger.error(f"Data transfer Failed for project : {project_name}")
                self.logger.info(f"Check logs for project  : {project_name} for more information")
                return False

            output = result.stdout.decode("utf-8")

            if result.returncode != 0:
                self.logger.debug(f"Data transfer logs for project - {project_name} - {output}")
                self.logger.info(f"Data transfer partially completed for project : {project_name}")
            else:
                self.logger.debug(f"Data transfer logs for project - {project_name} - {output}")
                self.logger.info(f"Data transfer completed for project : {project_name}")

            self.os_inst.remove_config_files(project_name)

            self.os_inst.ora2pg_error_log(project_name)
            return True
        else:
            self.logger.error(f"No table at target to Data transfer - Project : {project_name}")

    def deploy_by_load(self,project_name, file_name, file_path, continue_deployment):
        temp_path,success =self.config_instance.refresh_ora2pg_config(project_name)
        core_count = self.os_inst.cpu_core(file_name)
        if core_count <=2:
            command = fr"ora2pg -t LOAD -c {temp_path} -i {file_path} -j 2 "
        else:
            command = fr"ora2pg -t LOAD -c {temp_path} -i {file_path} -j {core_count} "
        result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
        output = result.stdout.decode("utf-8")
        if result.returncode != 0 and not continue_deployment:
            self.logger.debug(f"Post data deployment logs for project - {project_name} - {output}")
            self.logger.info(f"Post data deployment partially completed for project : {project_name} - File : {file_path}")
            return True
        else:
            self.logger.debug(f"Post data, deployment logs for project - {project_name} - {output}")
            self.logger.error(f"Post data deployment failed for project : {project_name} - File : {file_path}")
            return False

        

    def test(self,project_name,t):
        temp_path,success = self.config_instance.refresh_ora2pg_config(project_name)
        path = self.os_inst.ora2pg_test_report(project_name)
        file_name = fr"{t}.txt"
        output_path = self.os_inst.os_join(path,file_name)

        command = fr"ora2pg -t TEST -c {temp_path} > {output_path}"
        result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
        output = result.stdout.decode("utf-8")
        self.logger.info(f"ora2pg validation report generated successfully. \n Report : {output_path}")
        self.logger.debug(f"ora2pg test logs for project - {project_name} - {output}")
        self.os_inst.remove_config_files(project_name)

    def test_view(self,project_name,t):
        temp_path,success = self.config_instance.refresh_ora2pg_config(project_name)
        path = self.os_inst.ora2pg_test_report(project_name)
        file_name = fr"{t}.txt"
        output_path = self.os_inst.os_join(path,file_name)
        # print(fr"ora2pg -t TEST_VIEW -c {temp_path} >{output_path}")
        command = fr"ora2pg -t TEST_VIEW -c {temp_path} >{output_path}"
        result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
        output = result.stdout.decode("utf-8")
        self.logger.info(f"ora2pg view report generated successfully. \nReport : {output_path}")
        self.logger.debug(f"ora2pg test_view logs for project - {project_name} - {output}")

        self.os_inst.remove_config_files(project_name)
        
    def test_count(self,project_name,t):
        temp_path,success = self.config_instance.refresh_ora2pg_config(project_name)
        path = self.os_inst.ora2pg_test_report(project_name)
        file_name = fr"{t}.txt"
        output_path = self.os_inst.os_join(path,file_name)

        command = fr"ora2pg -t TEST_COUNT -c {temp_path} >{output_path}"
        result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
        output = result.stdout.decode("utf-8")
        self.logger.info(f"ora2pg count report generated successfully. \nReport : {path}")
        self.logger.debug(f"ora2pg test_count logs for project - {project_name} - {output}")
        self.os_inst.remove_config_files(project_name)
      
    def validate_ora2pg_version(self,project_name):
        if self.platform_inst.platform_name() == "Windows":
            result_version =os.system(fr"ora2pg -v > NUL 2>&1" )
            return result_version
        else:
            result_version =os.system(fr"export LC_ALL=C;ora2pg -v > /dev/null" )
            return result_version
        
    def check_ora2pg_version(self):
        command = r"ora2pg -v"
        result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
        output = result.stdout.decode("utf-8")
        pattern = r"Ora2Pg\sv[0-9]+\.[0-9]"
        match = re.search(pattern, output)
        matched = match.group(0)

        number_pattern = r"[0-9]+\.[0-9]"
        num_match = re.search(number_pattern, matched)
        num_matched = num_match.group(0)
        version = float(num_matched)
        return version

    def validate_ora2pg_table(self,project_name):
        result_table =self.show_table(project_name)
        return result_table
    
    def psql_version(self):
        if self.platform_inst.platform_name() == "Windows":
            version = os.system("psql -V > NUL 2>&1")
        else:
             version = os.system("export LC_ALL=C;psql -V > /dev/null")
        if version == 0:
            return True
        else:
            return False
        
class PsqlCommand:

    def __init__(self, project_name):
        self.project_name = project_name
        self.platform_inst = OSPlatform(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        self.config_instance = ConfigInputs(self.project_name)
        self.sqlite_inst = SqliteDatabaseManagement(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()
    
    def psql_deploy(self,password,host,username,db_name,port,stop_error,filepath,project_name):
        os_name = self.platform_inst.platform_name()
        if os_name == "Windows":
            command = fr"""set "PGPASSWORD={password}" && psql -h {host} -U {username} -d {db_name} -p {port}"""
            if stop_error in [0, 1]:
                if stop_error is not None:
                    command += fr" -v ON_ERROR_STOP={stop_error} -f {filepath}"
                else:
                    command += fr" -v ON_ERROR_STOP={self.sqlite_inst.fetch_stop_error(project_name)} -f {filepath}"

                result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT,  shell=True )
                if result.returncode !=0:
                    if result.stdout.strip() is not None:
                        output = result.stdout.decode("utf-8")
                        self.logger.debug(f"Unable to deploy File - {filepath} - Error - {output }")
                        return False;
            
                output = result.stdout.decode("utf-8") ;
                self.logger.debug(f"Deployment completed for - {filepath} - Msg - {output}")
                return True
            else:
                self.logger.error(f"Unable to deploy {filepath}\nON_ERROR_STOP only supports 0 or 1")
                return False
        
        else:
            command = fr"""PGPASSWORD={password} psql -h {host} -U {username} -d {db_name} -p {port}"""
            if stop_error is not None:
                command += fr" -v ON_ERROR_STOP={stop_error} -f {filepath}"
            else:
                command += fr" -v ON_ERROR_STOP={error_cnt} -f {filepath}"

            result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT,  shell=True )
            if result.returncode !=0:
                if result.stdout.strip() is not None:
                    output = result.stdout.decode("utf-8")
                    self.logger.debug(f"Unable to deploy File - {filepath} - Error - {output }")
                    return False;
                
            output = result.stdout.decode("utf-8") ;
            self.logger.debug(f"Deployment completed for - {filepath} - Msg - {output}")
            return True

    





    