from os_operation.ora2pg_commands import ora2pgCommand
from database_operation.oracle import OracleDatabaseManagement
from database_operation.postgres import PostgresDatabase
from dcgmigrator_core.logging_operation import HandleLogging

# from log_prac import HandleLogging

class ValidatePrerequisite:
    
    def __init__(self,project_name):
        self.project_name = project_name
        self.os_inst = ora2pgCommand(self.project_name)
        self.ora_inst = OracleDatabaseManagement(self.project_name)
        self.pg_inst = PostgresDatabase(self.project_name)
        log_inst = HandleLogging(self.project_name)
        self.logger = log_inst.handle_log()
        # self.logger = log_inst.log(file=False, console=True)
        
    def validate_ora2pg(self,project_name):
        result_version = self.os_inst.validate_ora2pg_version(project_name)
        # result_version = 1
        ora2pg_version = self.os_inst.check_ora2pg_version()
        #result_schema = self.os_inst.validate_ora2pg_schema(project_name)
        if result_version == 0:
            self.logger.info("ora2pg - Pass")
            if ora2pg_version < 23.2:
                self.logger.info(f"Your current ora2pg version - {ora2pg_version}. Please upgrade to ora2pg version 23.2 or higher")
            return True
        else:
            self.logger.error("Ora2pg check fail, please check or install Ora2pg Setup")
            return False
        
    def validate_oracle_connection(self,project_name):
        result_conn = self.ora_inst.validate_oracle(project_name)
        if result_conn:
            self.logger.info("oracle database connection - Pass")
            return True        
        else:
            self.logger.error("Oracle Connection failed, please check the connection details")
            return False

    def validate_oracle_schema_exists(self,project_name):
        result_conn = self.ora_inst.validate_oracle_schema(project_name)
        if result_conn:
            self.logger.info("Oracle schema to migrate exist - Pass")
            return True        
        else:
            self.logger.error("Oracle schema to migrate does not exists.")
            return False
        
    def validate_postgres_connection(self,project_name):
        try:
            result_conn = self.pg_inst.validate_postgres(project_name)
            if result_conn:
                self.logger.info("PostgreSQL database connection - Pass")
                return True
            else:
                self.logger.error("PostgreSQL Connection failed, please check the connection details")
                return False
        except Exception as e:
            self.logger.error("PostgreSQL Connection failed, please check the connection details")
            return False
            
        
    def validate_pg_user(self,project_name):
        success,user = self.pg_inst.pg_user(project_name)
    
        if success:
            self.logger.info(f"PostgreSQL user({user}) Exists - Pass")
            return True
        else:
            self.logger.error(f"Please add Postgres user {user} as per Oracle schema ")
            return False

    def validate_psql(self):
        version = self.os_inst.psql_version()
        
        if version:
            self.logger.info(f"psql command line is installed - Pass")
            return True
        else:
            self.logger.error(f"unable to find PosgreSQL - psql command line")
            return False

    def validate_prerequisite(self,project_name):
        try:
            print("\n----Checking Tools installation - Ora2pg and psql command line----\n")
            ora2pg_val = self.validate_ora2pg(project_name)
            psql = self.validate_psql()

            print("\n----Checking Source connections and Schema existance----\n")
            ora_conn = self.validate_oracle_connection(project_name)
            if ora_conn:
                ora_schema_exist = self.validate_oracle_schema_exists(project_name)

            print("\n----Checking Target connections and User existance----\n")
            pg_conn = self.validate_postgres_connection(project_name)
            if pg_conn:
                pg_user = self.validate_pg_user(project_name)

            if ora_conn == False or pg_conn == False or ora2pg_val == False or pg_user == False or psql == False or ora_schema_exist == False:
                self.logger.error(f"Pre check fails for migration project : {project_name}")
                return False

            else:
                self.logger.info(f"Pre check pass successfully for migration project : {project_name}")
                return True

        except Exception as e:
            self.logger.error(f"Pre-checks failed - {e.__cause__}")
            return False
        
          
        
