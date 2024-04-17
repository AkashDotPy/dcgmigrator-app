import platform
import os
from database_operation.postgres import PostgresDatabase

class OSPlatform:
    def __init__(self, project_name):
        self.project_name = project_name
        self.pg_inst = PostgresDatabase(project_name)

    def platform_name(self):
        os_name = platform.system()
        # os_name = "Windows"
        
        return os_name

    def psql_cmd(self,project_name,file_path):
        username,password,host,port,dbname,pg_schema = self.pg_inst.fetch_pg_cred_deploy(project_name)
        os.system(fr"psql${host}${port} -U ${pg_schema} -d ${dbname} -f ${file_path}")