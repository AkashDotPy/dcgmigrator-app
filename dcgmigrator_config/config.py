from database_operation.sqlite import SqliteDatabaseManagement
from database_operation.postgres import PostgresDatabase
from os_operation.os_handling import DirectoryPath
from database_operation.oracle import OracleDatabaseManagement

from dcgmigrator_core.logging_operation import HandleLogging

# self.os_inst = DirectoryPath()
# self.sqlite = SqliteDatabaseManagement()
# self.ora_inst = OracleDatabaseManagement()
# self.pg_inst = PostgresDatabase()
# log_instance = HandleLogging()
# self.logger = log_instance.handle_log()

class ConfigInputs:
    def __init__(self, project_name):
        self.project_name = project_name
        self.os_inst = DirectoryPath(self.project_name)
        self.sqlite = SqliteDatabaseManagement(self.project_name)
        self.ora_inst = OracleDatabaseManagement(self.project_name)
        self.pg_inst = PostgresDatabase(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def default_config(self,project_name):
        default_config_content = (
                                    {"project_name": f"{project_name}", "key": "EXPORT_SCHEMA"         , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"PKEY_IN_CREATE"        , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"KEEP_PKEY_NAMES"       , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"FKEY_ADD_UPDATE"       , "value":"never"},
                                    {"project_name": f"{project_name}", "key":"GEN_USER_PWD"          , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"FILE_PER_FKEYS"        , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"FILE_PER_CONSTRAINT"   , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"FILE_PER_INDEX"        , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"EXPORT_GTT"            , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"FILE_PER_FUNCTION"     , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"FORCE_OWNER"           , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"PACKAGE_AS_SCHEMA"     , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"PG_SUPPORTS_IDENTITY"  , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"PG_SUPPORTS_PROCEDURE" , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"NO_EXCLUDED_TABLE"     , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"EXTERNAL_TO_FDW"       , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"TRUNCATE_TABLE"        , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"USE_TABLESPACE"        , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"DROP_IF_EXISTS"        , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"DISABLE_SEQUENCE"      , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"DISABLE_UNLOGGED"      , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"STOP_ON_ERROR"         , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"CREATE_OR_REPLACE"     , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"PG_INTEGER_TYPE"       , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"PG_NUMERIC_TYPE"       , "value":"0"},
                                    {"project_name": f"{project_name}", "key":"DEFAULT_NUMERIC"       , "value":"double precision"},
                                    {"project_name": f"{project_name}", "key":"VARCHAR_TO_TEXT"       , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"FORCE_IDENTITY_BIGINT" , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"DATA_EXPORT_ORDER"     , "value":"size"},
                                    {"project_name": f"{project_name}", "key":"PSQL_RELATIVE_PATH"    , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"PARALLEL_MIN_ROWS"     , "value":"500000"},
                                    {"project_name": f"{project_name}", "key":"PLSQL_PGSQL"           , "value":"1"},
                                    {"project_name": f"{project_name}", "key":"NULL_EQUAL_EMPTY"           , "value":"1"}
        )
        return self.insert_ora2pgconfigs(project_name,default_config_content)
    
    def insert_ora_home(self):
        oracle_home = self.os_inst.ora_home()
        if oracle_home == "" or oracle_home == None:
            return self.logger.error("Unable to extract ORACLE_HOME \n Please set environment or insert it manually using command : update config")
        else:
            return oracle_home
    
    def oracle_cred(self,project_name,oracle_home,ora_host,ora_service_name,ora_port,ora_user,ora_pwd,ora_schema):
        oracle_home = self.insert_ora_home()
        ora_config_content = (
                                {"project_name": f"{project_name}","key":"ORACLE_HOME"   , "value":f"{oracle_home}"},
                                {"project_name": f"{project_name}","key":"ORACLE_DSN"    , "value":f"dbi:Oracle:host={ora_host};service_name={ora_service_name};port={ora_port}"},
                                {"project_name": f"{project_name}","key":"ORACLE_USER"   , "value":f"{ora_user}"},
                                {"project_name": f"{project_name}","key":"ORACLE_PWD"    , "value":f"{ora_pwd}"},
                                {"project_name": f"{project_name}","key":"ORA_SCHEMA"    , "value":f"{ora_schema}"},
                                {"project_name": f"{project_name}","key":"PG_SCHEMA"     , "value":f"{ora_schema.lower()}"},       
                                {"project_name": f"{project_name}","key":"SCHEMA"        , "value":f"{ora_schema}"}
        )
        return self.insert_ora2pgconfigs(project_name,ora_config_content)

    def pg_cred(self,project_name,pg_dbname,pg_host,pg_port,pg_user,pg_password,input_pg_version):
        # if input_pg_version == None: 
        #     pg_version = self.pg_inst.pg_version(project_name)
        #     print(pg_version)
        # else:
        #     pg_version = input_pg_version
        
        pg_config_content = ( 
                                {"project_name": f"{project_name}","key":"PG_DSN"    , "value":f"dbi:Pg:dbname={pg_dbname.lower()};host={pg_host};port={pg_port}"},
                                {"project_name": f"{project_name}","key":"PG_USER"   , "value":f"{pg_user.lower()}"},
                                {"project_name": f"{project_name}","key":"PG_PWD"    , "value":f"{pg_password}"},
                                {"project_name": f"{project_name}","key":"PG_VERSION", "value":f"{input_pg_version}"} 
        )
        
        return self.insert_ora2pgconfigs(project_name, pg_config_content)
    
    # def pg_version(self,project_name):
    #     pg_version = self.pg_inst.pg_version(project_name)
    #     self.sqlite.update_pg_version(project_name,pg_version)

            
    def insert_ora2pgconfigs(self, project_name, config_content):
        if self.sqlite.insert_ora2pgconfig_many(project_name, config_content):
            self.logger.info(f"Necessary ora2pg config inserted successfull for project : {project_name}")
            return True
        else:
            self.logger.info(f"Necessary ora2pg config insertion failed for project : {project_name}")
            return False
         
    def refresh_ora2pg_config(self,project_name):
        result = self.sqlite.refresh_ora2pgconfig(project_name)
        path, parent_directory = self.os_inst.config_path(project_name)

        with open(path, 'w') as configfile:
            for key, value in result:
                configfile.write(f"{key}    {value}\n")
        return path,True

    def refresh_ora2pg_config_withoutpasswd(self,project_name):
        result = self.sqlite.generate_config(project_name)
        path, parent_directory = self.os_inst.config_path(project_name)

        with open(path, 'w') as configfile:
            for key, value in result:
                configfile.write(f"{key}    {value}\n")
        self.logger.info(f"Necessary config generated successfull for project : {project_name} at path - {path}")
        self.logger.info(f"Password for databases is intentionally not included")
        return path
    
    
    def validate_view_count(self,project_name):
        self.data = {}
        result = self.ora_inst.view_count(project_name)
      
        if result =="Y":
              update = {"NO_VIEW_ORDERING" : "0"}
              self.data.update(update)

        if result =="N":
            update = {"NO_VIEW_ORDERING" : "1"}
            self.data.update(update)

        for key, value in self.data.items():
            self.sqlite.insert_ora2pgconfig(project_name, key, value)
        
        self.refresh_ora2pg_config(project_name)
        self.logger.info(f"Necessary additional config {self.data}  for projects  {project_name} inserted successfully")


        
    




      
        
