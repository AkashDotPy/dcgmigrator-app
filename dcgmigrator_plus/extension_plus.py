from database_operation.postgres import PostgresDatabase
from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_core.logging_operation import HandleLogging
from dcgmigrator_config.config import ConfigInputs

class Extention:

    def __init__(self,project_name):
        self.project_name = project_name
        self.data = {}
        self.pg_inst = PostgresDatabase(self.project_name)
        self.sqlite = SqliteDatabaseManagement(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.config_inst = ConfigInputs(self.project_name)
        self.logger = log_instance.handle_log()

    def extension_command(self,project_name):

        orafce = self.pg_inst.orafce(project_name)
        gtt = self.pg_inst.export_gtt(project_name)
        dblink = self.pg_inst.dblink_conn(project_name)
        pgbackground = self.pg_inst.autonomous_transaction_pg_background(project_name)
        fdw = self.pg_inst.oracle_fdw(project_name)
        extension_command = ""
        if orafce:
            extension_command += "create extension IF NOT EXISTS orafce;" + "\n"
        if gtt:
            extension_command += "create extension IF NOT EXISTS pgtt;" + "\n"
        if pgbackground:
            extension_command += "create extension IF NOT EXISTS pg_background;" + "\n"
        if fdw:
            extension_command += "create extension IF NOT EXISTS oracle_fdw;" + "\n"
        if dblink:
            extension_command += "create extension IF NOT EXISTS dblink;" + "\n"
        return extension_command

    def extension_flag(self,project_name):
        orafce = self.pg_inst.orafce(project_name)
        gtt = self.pg_inst.export_gtt(project_name)
        dblink = self.pg_inst.dblink_conn(project_name)
        pgbackground = self.pg_inst.autonomous_transaction_pg_background(project_name)
        autonomous = dblink
        
        if orafce:
            update ={"USE_ORAFCE" : "1"}
            self.data.update(update)

        if gtt:
            update ={"EXPORT_GTT" : "1"}
            self.data.update(update)

        if pgbackground:
            update ={"PG_BACKGROUND" : "1"}
            self.data.update(update)

        if autonomous:
            update ={"AUTONOMOUS_TRANSACTION" : "1"}
            self.data.update(update)
        
        return self.data
    
    def oracle_fdw_flag(self, project_name):
        fdw = self.pg_inst.oracle_fdw(project_name)
        if fdw:
            update ={"FDW_SERVER" :  "orcl",
                    "FDW_IMPORT_SCHEMA" : "ora2pg_fdw_import"}
            self.data.update(update)
        return self.data

    def insert_config(self,data, project_name):
        for key, value in data.items():
            self.sqlite.insert_ora2pgconfig(project_name, key, value)
        
        self.config_inst.refresh_ora2pg_config(project_name)
        self.logger.info(f"\nNecessary additional PostgreSQL Extension related config {data}  for projects:{project_name} inserted successfully")

    def extention_plus(self,project_name):
        data = self.extension_flag(project_name)
        if len(data) > 0:
            self.insert_config(data, project_name)
            return True
        else:
            return False

    def oracle_fdw_plus(self,project_name):
        data = self.oracle_fdw_flag(project_name)
        self.insert_config(data, project_name)

