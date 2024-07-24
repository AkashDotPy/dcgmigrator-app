import numpy as np
import multiprocessing 
import subprocess as sp
import os
from os_operation.os_handling import DirectoryPath
from database_operation.sqlite import SqliteDatabaseManagement
from database_operation.postgres import PostgresDatabase
from database_operation.oracle import OracleDatabaseManagement
from dcgmigrator_plus.extension_plus import Extention
from dcgmigrator_config.config import ConfigInputs 
from dcgmigrator_core.logging_operation import HandleLogging

class DataTransfer:
    def __init__(self, project_name):
        self.project_name = project_name
        self.os_inst = DirectoryPath(project_name)
        self.sqlite_inst = SqliteDatabaseManagement(self.project_name)
        self.ora_inst = OracleDatabaseManagement(self.project_name)
        self.pg_inst = PostgresDatabase(self.project_name)
        self.extension_plus = Extention(self.project_name)
        self.config_instance = ConfigInputs(self.project_name)
        log_instance = HandleLogging(project_name)
        self.logger = log_instance.handle_log()
        
    def filter_tables(self, project_name):
        result =  self.ora_inst.data_migration_chunks(project_name, self.pg_inst.fetch_table_exists(project_name))
        self.logger.info(f"Data Migration Table Distribution Information")
        for chunks in result:
            self.logger.info(f"Chunk : {chunks[0]} , Tables List : {chunks[2]} ")
        return result
    
    @staticmethod
    def data_transfer(chunk ,temp_path, file_name, project_name, use_oraclefdw ,continue_on_error ,data_limit):
        log_instance = HandleLogging(project_name)
        logger = log_instance.handle_log()
        os_inst = DirectoryPath(project_name)
        #run only for migrated tables   
        if not chunk is None:
            logger.info(f"Data transfer begin for project : {project_name} with pid : {os.getpid()} .......\nMigrating tables : {chunk}\n")
            command = fr"ora2pg -t COPY -c {temp_path} -a {chunk} " + (' -W "ROWNUM < ' + str(data_limit + 1) + '"'  if data_limit is not None else "")
            result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
            if result.returncode != 0  and not continue_on_error:
                output = result.stdout.decode("utf-8")
                logger.debug(f"Data transfer logs - Project : {project_name} with pid : {os.getpid()} - {output}")
                logger.error(f"Data transfer Failed for project : {project_name} with pid : {os.getpid()}")
                logger.info(f"Check logs for project  : {project_name} for more information")
                return False

            output = result.stdout.decode("utf-8")

            if result.returncode != 0:
                logger.debug(f"Data transfer logs for project - {project_name} with pid : {os.getpid()} - {output}")
                logger.info(f"Data transfer partially completed for project : {project_name} with pid : {os.getpid()}\nMigrated tables : {chunk}\n")
            else:
                logger.debug(f"Data transfer logs for project - {project_name} with pid : {os.getpid()} - {output}")
                logger.info(f"Data transfer completed for project : {project_name} with pid : {os.getpid()}\nMigrated tables : {chunk}\n")

            os_inst.remove_multi_config_files(file_name, project_name)

            os_inst.ora2pg_error_log(project_name)
            return True
        else:
            logger.error(f"No table at target to Data transfer - Project : {project_name}")


    def multiprocess_copy(self, project_name, use_oraclefdw ,continue_on_error ,data_limit):
        process = []
        chunks = self.filter_tables(project_name)
        dir_path,parent_directory = self.os_inst.config_path(project_name)
        
        if use_oraclefdw:
            self.extension_plus.oracle_fdw_flag(project_name)
        
        if continue_on_error:
            self.sqlite_inst.insert_ora2pgconfig(project_name,"LOG_ON_ERROR","1")
        else:
             self.sqlite_inst.remove_config(project_name,"LOG_ON_ERROR")
        self.sqlite_inst.update_config("DATA_VALIDATION_ROWS", data_limit if data_limit is not None else 10000, project_name)
        
        temp_path,success = self.config_instance.refresh_ora2pg_config(project_name)

        with open (temp_path, 'r') as file:
            data = file.read()

        try:
            for index, chunk in enumerate(chunks,1):
                file_name = f"{project_name}_ora2pg_{index}.conf"
                multi_config_path = self.os_inst.os_join(parent_directory,file_name)

                #Data Migration Rules
                #Bases on Chunks no, we will defined config and changed some of the data_limit properties.
                ora2pg_conf_props = {
                    1: f"DATA_LIMIT   300000\nPK_DEFINED {chunk[1]}\nORACLE_COPIES    2\nJOBS    1""",
                    2:f"DATA_LIMIT  2000\nPK_DEFINED {chunk[1]}\nORACLE_COPIES    2\nJOBS    1""",
                    3:f"DATA_LIMIT  2000\nPARALLEL_TABLES 2",  
                    4:f"DATA_LIMIT  200000\nPARALLEL_TABLES 2",   
                    5:f"DATA_LIMIT  5200000\nPARALLEL_TABLES 2",         
                    6:f"DATA_LIMIT  2000\nPARALLEL_TABLES 2"
                }
                
                with open (multi_config_path, 'w') as f:
                    f.write(data + ora2pg_conf_props.get(chunk[0], ""))

                p1 = multiprocessing.Process(target=DataTransfer.data_transfer, args= (chunk[2] ,multi_config_path, file_name, project_name,use_oraclefdw , continue_on_error , data_limit))
                p1.start()
                
                if not chunk[0] in (5,6): #control multi-process in parallel, currently will run only for 5 and 6.
                    process = []
                    process.append(p1)
                    for p in process:
                        p.join()
                else:
                    process.append(p1)
            
            for p in process:
                p.join()

            return True
        except Exception as e:
            self.logger.error(f"Unable to data transfer with multiprocess  for project : {project_name} : Error : {e.__cause__}")
            return False