from database_operation.sqlite import SqliteDatabaseManagement
import os
import sys

class DcgMigrator_Command:

    def __init__(self,project_name):
        self.project_name = project_name
        self.sqlite_instance = SqliteDatabaseManagement(project_name)
        
    def prereq_cmd(self):
        return os.system(fr"python dcgmigrator.py dcgmigrator test-prerequisite --project_name {self.project_name}")
    
    def convert_cmd(self):
        status = self.sqlite_instance.fetch_status(self.project_name)
        if status == "pre-check pass":
            return os.system(fr"python dcgmigrator.py dcgmigrator convert --project_name {self.project_name}")
        else:
            print("cannot proceed further")

    def deploy_predata_cmd(self):
        status = self.sqlite_instance.fetch_status(self.project_name)
        if status == "converted":
            return os.system(fr"python dcgmigrator.py dcgmigrator deploy --type pre-data  --project_name {self.project_name}")
        else:
            print("cannot proceed further")

    def copy_cmd(self):
        status = self.sqlite_instance.fetch_status(self.project_name)
   
        if status == "deployed-pre-data":
            return os.system(fr"python dcgmigrator.py dcgmigrator copy --project_name {self.project_name}")
        else:
            print("cannot proceed further")

    def deploy_postdata_cmd(self):
        status = self.sqlite_instance.fetch_status(self.project_name)
        if status == "data transfer":
            return os.system(fr"python dcgmigrator.py dcgmigrator deploy --type post-data  --project_name {self.project_name}")
        else:
            print("cannot proceed further")

    def test_migrator_cmd(self):
        status = self.sqlite_instance.fetch_status(self.project_name)
        if status == "deployed-post-data":
            os.system(fr"python dcgmigrator.py dcgmigrator test-migrator --t schema --project_name {self.project_name}")
            os.system(fr"python dcgmigrator.py dcgmigrator test-migrator --t trigger --project_name {self.project_name}")
            os.system(fr"python dcgmigrator.py dcgmigrator test-migrator --t code --project_name {self.project_name}")
            os.system(fr"python dcgmigrator.py dcgmigrator test-migrator --t test_ora2pg --project_name {self.project_name}")
            os.system(fr"python dcgmigrator.py dcgmigrator test-migrator --t test_count_ora2pg --project_name {self.project_name}")
            return os.system(fr"python dcgmigrator.py dcgmigrator test-migrator --t test_view_ora2pg  --project_name {self.project_name}")

