from os_operation.ora2pg_commands import ora2pgCommand
from os_operation.os_handling import DirectoryPath
from dcgmigrator_plus.ora2pg_plus import Plus
from dcgmigrator_config.config import ConfigInputs 
from database_operation.oracle import OracleDatabaseManagement
from dcgmigrator_core.logging_operation import HandleLogging

class Convert:
    def __init__(self,project_name):
        self.project_name = project_name
        self.plus_instance = Plus(self.project_name)
        self.ora2pg = ora2pgCommand(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        self.conf_inst = ConfigInputs(self.project_name)
        self.ora_inst = OracleDatabaseManagement(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()
        
    def convert(self,project_name, type, rundatatypemapping=True):
        dir_path = self.os_inst.convert_output_dir(project_name)
        ora_obj = self.ora_inst.oracle_objects(project_name)
        ora_obj_dict = dict(ora_obj)
        ora_obj_list = list(ora_obj_dict.keys())
        sorted_ora_obj = dict(sorted(ora_obj_dict.items(), key=lambda item: item[1]))

        if type == None:
            try:
                for type, value in sorted_ora_obj.items():
                    self.logger.info(f"\n Started converting - {type} object.")

                    if "SEQUENCE_VALUES".casefold() in type.casefold():
                        self.logger.info(f"Skipping {type}")
                        continue

                    if "TABLE".casefold() in type.casefold():

                        if rundatatypemapping:
                            if self.plus_instance.modify_type(project_name):
                                 self.logger.info("\n Data Type Mapping updated in config succesfully")
                            else:
                                self.logger.error(f"Update of modify type failed.") 
                                return False
                        if self.plus_instance.extension(project_name):
                            #adding option to generate Extension Command as part of Conversion
                            with open(self.os_inst.os_join(self.os_inst.convert_output_dir(project_name),"EXTENSION.sql"), "w") as sqlfile:
                                sqlfile.write(self.plus_instance.extension_command(project_name))

                    if "VIEW".casefold() in type.casefold():
                        self.conf_inst.validate_view_count(project_name)

                    self.ora2pg.convertion(project_name,type)
                    self.logger.info(f"\n Conversion of database - {type} object is successfully done")
                self.logger.info("\n Conversion of Schema is successfully done")
                self.logger.info(f"Converted files are stored : {dir_path}")
                self.os_inst.remove_config_files(project_name)
                return True
            except Exception as e:
               self.os_inst.remove_config_files(project_name)
               self.logger.error(f"{e}\nIssue occoured while conversion")
               return False

        elif type.upper() in set(ora_obj_dict.keys()):
            try:
                self.logger.info(f"Strated converting - {type} object")
                if type.casefold() == "TABLE".casefold():
                    if rundatatypemapping:
                        if self.plus_instance.modify_type(project_name):
                             self.logger.info("\n Data Type Mapping updated in config succesfully")
                        else:
                            self.logger.error(f"Update of modify type failed.") 
                            return False
                    if self.plus_instance.extension(project_name):
                        #adding option to generate Extension Command as part of Conversion
                        with open(self.os_inst.os_join(self.os_inst.convert_output_dir(project_name),"EXTENSION.sql"), "w") as sqlfile:
                            sqlfile.write(self.plus_instance.extension_command(project_name))

                if type.casefold() == "VIEW".casefold():
                    self.conf_inst.validate_view_count(project_name)

                self.ora2pg.convertion(project_name,type.upper())
                self.logger.info(f"\n Conversion of database - {type} object is successfully done")
                self.os_inst.remove_config_files(project_name)
                return True
            except Exception as e:
                self.os_inst.remove_config_files(project_name)
                self.logger.error(f"{e}\nIssue occoured while conversion")
                return False

        else:
            self.logger.error(f"Specified convertion database type is missing from Database -  {list(ora_obj_dict.keys())}")
            return False
    

    


        
        

    
        
    
