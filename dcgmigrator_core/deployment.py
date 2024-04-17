from database_operation.postgres import PostgresDatabase
from database_operation.oracle import OracleDatabaseManagement
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.conversion import Convert
from dcgmigrator_core.logging_operation import HandleLogging
from os_operation.ora2pg_commands import ora2pgCommand,PsqlCommand
from os_operation.os_platform import OSPlatform
from dcgmigrator_core.migrator_validation import MigratorValidation

class deployment:
    ora2pg_flag = True
    ora2pg_load_obj = ["FKEYS", "INDEXES"]

    def __init__(self, project_name):
        self.project_name = project_name
        self.pg_inst = PostgresDatabase(self.project_name)
        self.ora_inst = OracleDatabaseManagement(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        self.obj_inst = Convert(self.project_name)
        self.ora2pg = ora2pgCommand(self.project_name)
        self.psql_inst = PsqlCommand(self.project_name)
        platfrom_inst = OSPlatform(self.project_name)
        self.os_name = platfrom_inst.platform_name()
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()
        self.val_inst = MigratorValidation(project_name)
                  
    def pre_data_deployment(self,stop_error,project_name,continue_deployment):
        username,password,host,port,dbname,pg_schema = self.pg_inst.fetch_pg_cred_deploy(project_name)
        pre_data_dp_order = self.ora_inst.pre_data_obj(project_name)
        if pre_data_dp_order:
            pre_obj_dict = dict(pre_data_dp_order)
            pre_obj_list = list(pre_obj_dict.keys())
            self.logger.info(f"\n Project - {project_name} : has below objects to Pre deploy \n {pre_obj_list}")

            dir_path = self.os_inst.convert_output_dir(project_name)
            dir_files = self.os_inst.files_in_output(dir_path)

            for key in pre_obj_list:
                self.logger.info(f"\n Starting deployment of - {key}")
                if self.os_name != "Windows":
                    if key not in deployment.ora2pg_load_obj:
                        matching_files = [file for file in dir_files if file.startswith(key)]
                        if matching_files:
                            # file_path = fr"{dir_path}/{file_name}"
                            file_name = matching_files[0]
                            file_path = self.os_inst.os_join(dir_path,file_name)

                            if deployment.ora2pg_flag == True:
                                #try:
                                    checkDeploy = self.psql_inst.psql_deploy(password,host,username,dbname,port,stop_error,file_path,project_name)
                                    if checkDeploy:
                                        self.logger.info(f"{file_name} : successfully deployed")
                                    else:
                                        if not continue_deployment: 
                                            self.logger.error(f"{file_name} : Failed")
                                            return False
                                        else:
                                            self.logger.error(f"{file_name} : deployed failed, please check project - {project_name} log files!")

                                #except Exception as e:
                                #    self.logger.error(f"Issue occured while deployment : {file_name} \n {e.__cause__}")

                            # else:
                            #     file_path = self.os_inst.os_join(dir_path,file_name)
                            #     with open(file_path, 'r') as file:
                            #         sql_file = file.read()
                            #         deploy_res = self.pg_inst.dep_execution_conn(project_name,sql_file)
                            #         if not deploy_res:
                            #             self.logger.error(f"Deployment Failed for Db type - {key}")
                            #             break
                            #         else:
                            #             self.logger.info(f"\n Completed Deployment for Db type - {key} - for project - {project_name}")

                    elif key in deployment.ora2pg_load_obj:
                        matching_files = [file for file in dir_files if file.startswith(key)]
                        if matching_files:
                            file_name = matching_files[0]
                            file_path = self.os_inst.os_join(dir_path,file_name)

                            if deployment.ora2pg_flag == True:
                                    load = self.ora2pg.deploy_by_load(project_name, file_name, file_path)
                                    if load == 0:
                                        self.logger.info(f"{file_name} : successfully deployed using ora2pg load")
                                    else:
                                        self.logger.error(f"\n Issue occured while deployment : {file_name}")
                else:
                    matching_files = [file for file in dir_files if file.startswith(key)]


                    if matching_files:
                        file_name = matching_files[0]
                        # file_path = fr"{dir_path}\{file_name}"
                        file_path = self.os_inst.os_join(dir_path,file_name)

                        if deployment.ora2pg_flag == True:
                            if self.psql_inst.psql_deploy(password,host,username,dbname,port,stop_error,file_path,project_name):
                                self.logger.info(f"{file_name} : successfully deployed")

            return True
        else:
            self.logger.info(f"\n Project - {project_name} : has no objects to Pre deploy ")
                       

    def post_data_deployment(self,stop_error,project_name,continue_deployment):
        username,password,host,port,dbname,pg_schema = self.pg_inst.fetch_pg_cred_deploy(project_name)
        post_data_dp_order = self.ora_inst.post_data_obj(project_name)
        if post_data_dp_order:
            post_obj_dict = dict(post_data_dp_order)
            post_key = list(post_obj_dict.keys())

            self.logger.info(f"{project_name} : has below objects to post deploy \n {post_key}")

            if "SEQUENCE_VALUES" in post_key: 
                self.ora2pg.convertion(project_name,"SEQUENCE_VALUES")
                self.logger.info(f"\n Conversion of database - SEQUENCE_VALUES  object is successfully done")
            else:
                self.logger.info("No - SEQUENCE_VALUES  object found in oracle database")

            dir_path = self.os_inst.convert_output_dir(project_name)
            dir_files = self.os_inst.files_in_output(dir_path)

            for key in post_key:
                if "TRIGGER_SANITY" == key: 
                    self.val_inst.test_migrator("trigger")
                    self.logger.info(f"\n Trigger sanity on project - {project_name} is completed")
                    continue

                if self.os_name != "Windows":
                    if key not in deployment.ora2pg_load_obj:
                        matching_files = [file for file in dir_files if file.startswith(key)]

                        if matching_files:
                            file_name = matching_files[0]
                            file_path = self.os_inst.os_join(dir_path,file_name)
                            if deployment.ora2pg_flag == True:
                                try:
                                    self.psql_inst.psql_deploy(password,host,username,dbname,port,stop_error,file_path,project_name)
                                    self.logger.info(f"{file_name} : successfully deployed")

                                except Exception as e:
                                    self.logger.error(f"Issue occured while deployment : {file_name} \n {e.__cause__}")

                            else:
                                path = self.os_inst.os_join(dir_path,file_name)
                                with open(path, 'r') as file:
                                    sql_file = file.read()
                                    deploy_res = self.pg_inst.dep_execution_conn(project_name,sql_file)
                                    if not deploy_res:
                                        self.logger.error(f"Deployment Failed for Db type - {key}")
                                    else:
                                        self.logger.info(f"\n Completed Deployment for Db type - {key} - for project - {project_name}")

                    elif key in deployment.ora2pg_load_obj:
                        matching_files = [file for file in dir_files if file.startswith(key)]

                        if matching_files:
                            file_name = matching_files[0]
                            file_path = self.os_inst.os_join(dir_path,file_name)
                            if deployment.ora2pg_flag == True:
                                    load = self.ora2pg.deploy_by_load(project_name, file_name, file_path,continue_deployment)
                                    if load:
                                        self.logger.info(f"{file_name} : successfully deployed using ora2pg load")
                                    # logger.info(f"{file_name} : successfully deployed by ora2pg load")
                                    else:
                                        self.logger.error(f"Issue occured while deployment : {file_name}")
                                        if not continue_deployment:
                                            return False

                else:
                    matching_files = [file for file in dir_files if file.startswith(key)]
                    if matching_files:
                        file_name = matching_files[0]
                        file_path = self.os_inst.os_join(dir_path,file_name)

                        if deployment.ora2pg_flag == True:
                            try:
                                self.psql_inst.psql_deploy(password,host,username,dbname,port,stop_error,file_path,project_name)
                                self.logger.info(f"{file_name} : successfully deployed")

                            except Exception as e:
                                self.logger.error(f"\n Issue occured while deployment : {file_name} \n {e.__cause__}")
            return True
        else:
            self.logger.info(f"{project_name} : has no objects to deploy post copy data\n")






