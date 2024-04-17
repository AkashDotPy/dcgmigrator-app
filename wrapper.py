from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_config.config import ConfigInputs 
from dcgmigrator_core.update_status import StatusUpdate
import subprocess as sp
import re
import json

class DcgWrapper:
    def __init__(self,project_name):
        self.project_name = project_name
        self.sqlite_inst = SqliteDatabaseManagement(self.project_name)
        self.config_instance = ConfigInputs(self.project_name)
        self.status_inst = StatusUpdate(project_name)
        self.config_instance = ConfigInputs(project_name)

    def create_project_wrapper(self, project_name, source, target):
        if self.sqlite_inst.create_project(project_name, source, target):
            self.status_inst.update_status("create-project",project_name)
            data = {"Status" : "project is created successfully"}
            return data
        else:
            data = {"Status" : "Unable to create project"}
            return data
        
    def create_source_wrapper(self, project_name,ora_home,ora_host,ora_service_name,ora_port,ora_user,ora_pwd,ora_schema):
        self.config_instance.default_config(project_name)
        self.config_instance.oracle_cred(project_name,ora_home,ora_host,ora_service_name,ora_port,ora_user,ora_pwd,ora_schema)
        return {"Status" : "Source is created"}
    
    def create_target_wrapper(self, project_name,pg_dbname,pg_host,pg_port,pg_user,pg_password,input_pg_version):
        self.config_instance.default_config(project_name)
        self.config_instance.pg_cred(project_name,pg_dbname,pg_host,pg_port,pg_user,pg_password,input_pg_version)
        return {"Status" : "Target is created"}
    
    def show_project_wrapper(self,project_name):
        print(project_name)
        df = self.sqlite_inst.fetch_project(project_name)
        # print(self.sqlite_inst.fetch_project(project_name))
        data = df.to_json(orient='records') 
        new_df = json.loads(data)
        return new_df
    
    def show_config_wrapper(self,project_name):
        result = self.sqlite_inst.show_config_jsonarray(project_name)
        return result
    
    def show_schema_wrapper(self,project_name):
        path,success = self.config_instance.refresh_ora2pg_config(project_name)
        if success:
            command = fr"ora2pg -t SHOW_SCHEMA  -c {path}"
            result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
            output = result.stdout.decode("utf-8")
            data = re.search(r"perl:(.*?)\(\"English_India\.1252\"\)\.", output, re.DOTALL | re.MULTILINE)
            data1 = data.group(0)
            result_string = re.sub(re.escape(data1), "", output).strip()
            multiline_result = result_string.replace('\n', '\n')
            return multiline_result
        
    def show_column_wrapper(self,project_name):
        path,success = self.config_instance.refresh_ora2pg_config(project_name)
        if success:
            command = fr"ora2pg -t SHOW_COLUMN  -c {path}"
            result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
            output = result.stdout.decode("utf-8")
            data = re.search(r"perl:(.*?)\(\"English_India\.1252\"\)\.", output, re.DOTALL | re.MULTILINE)
            data1 = data.group(0)
            result_string = re.sub(re.escape(data1), "", output).strip()
            return result_string
        
    def show_table_wrapper(self,project_name):
        path,success = self.config_instance.refresh_ora2pg_config(project_name)
        if success:
            command = fr"ora2pg -t SHOW_TABLE  -c {path}"
            result = sp.run(command, stdout=sp.PIPE,stderr=sp.STDOUT, shell=True )
            output = result.stdout.decode("utf-8")
            data = re.search(r"perl:(.*?)\(\"English_India\.1252\"\)\.", output, re.DOTALL | re.MULTILINE)
            data1 = data.group(0)
            result_string = re.sub(re.escape(data1), "", output).strip()
            return result_string
