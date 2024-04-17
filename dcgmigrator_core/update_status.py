from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_core.prerequisite import ValidatePrerequisite
from dcgmigrator_core.logging_operation import HandleLogging
class StatusUpdate:

    def __init__(self,project_name):
        self.project_name = project_name
        self.sqlite_inst = SqliteDatabaseManagement(self.project_name)
        self.pre_inst = ValidatePrerequisite(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def update_status(self,subcommand,project_name):
        stage_values = {
            "create-project": "initialized_project",
            "create-source": "initialized_source",
            "create-target": "initialized_target",
            "test-prerequisite" : "precheck_completed",
            "convert table": "converted",
            "deploy pre-data": "deployed-pre-data",
            "copy": "data transfer",
            "deploy post-data": "deployed-post-data",
            "validate" : "validated"
        }

        for key, value in stage_values.items():
            if subcommand.lower() in key.lower():
                try:
                    if not self.sqlite_inst.update_project_status(value,project_name):
                        self.logger.error(f"Failed to update status for project : {project_name}")
                    
                except Exception as e:
                    self.logger.error(f"{e}issue occured in {subcommand} process")
                    raise e

        return key, value            

    def pre_check_status(self,subcommand,project_name):
      
        if self.pre_inst.validate_prerequisite(project_name) == True :   
            value = "pre-check pass"
            self.sqlite_inst.update_project_status(value,project_name)
            return True
        else:
            value = "pre-check fail"
            self.sqlite_inst.update_project_status(value,project_name)
            return False
            

    


    

         