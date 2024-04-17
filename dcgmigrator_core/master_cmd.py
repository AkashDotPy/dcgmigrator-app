from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_config.config import ConfigInputs
from os_operation.ora2pg_commands import ora2pgCommand
from dcgmigrator_core.conversion import Convert
from dcgmigrator_core.deployment import deployment
from schema_validation.validation import Validation
from trigger_sanity.trigger_sanity import TestTrigger
from code_sanity.code_sanity import TestCode
from dcgmigrator_core.update_status import StatusUpdate
from dcgmigrator_core.command_flow import CommandFlowManager
from dcgmigrator_core.logging_operation import HandleLogging
from os_operation.dcgmigrator_commands import DcgMigrator_Command
import sys
from tqdm import tqdm
import time

class MasterCommand:

    def __init__(self,project_name):
        self.project_name = project_name
        self.cmd = ora2pgCommand(project_name)
        self.config_instance = ConfigInputs(project_name)
        self.sqlite_instance = SqliteDatabaseManagement(project_name)
        self.conv_instance = Convert(project_name)
        self.deploy_inst = deployment(project_name)
        self.schema_inst = Validation(project_name)
        self.trigger_inst = TestTrigger(project_name)
        self.code_inst = TestCode(project_name)
        self.status_inst = StatusUpdate(project_name)
        self.cmd_flow_inst = CommandFlowManager(project_name)
        self.dcg_inst = DcgMigrator_Command(project_name)

        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()
        
    def master_cmd(self,project_name):
        stage = {
                "test-prerequisite" : "pre-check pass",
                "convert"           : "converted",
                "deploy pre-data"   : "deployed-pre-data",
                "copy"              : "data transfer",
                "deploy post-data"  : "deployed-post-data",
                "test-migrator"     : "validated"
                }

        
        stage_key = list(stage.keys())
        stage_value = list(stage.values())

        status = self.sqlite_instance.fetch_status(project_name)

        for subcommand in tqdm(stage_key, desc = f"Processing Stage"):
            
            if subcommand == "test-prerequisite":
                self.logger.info(fr"Begining stage : {subcommand}......")
               
                if self.dcg_inst.prereq_cmd() == 0:
                    self.logger.info(fr"Completion of stage : {subcommand}")    
                else:
                    self.logger.error(fr"Failure of stage : {subcommand}")
                    sys.exit(1)

            if subcommand == "convert": 
                
                self.logger.info(fr"Begining stage : {subcommand}......")
                if self.dcg_inst.convert_cmd() == 0:
                    self.logger.info(fr"Completion of stage : {subcommand}")
                else:
                    self.logger.error(fr"Failure of stage : {subcommand}")
                    sys.exit(1)

            if subcommand == "deploy pre-data":
                self.logger.info(fr"Begining stage : {subcommand}......")
                if self.dcg_inst.deploy_predata_cmd() == 0:
                    self.logger.info(fr"Completion of stage : {subcommand}")
                else:
                    self.logger.error(fr"Failure of stage : {subcommand}")
                    sys.exit(1)

            if subcommand == "copy":
                self.logger.info(fr"Begining stage : {subcommand}......")
                if self.dcg_inst.copy_cmd() == 0 :
                    self.logger.info(fr"Completion of stage : {subcommand}")
                else:
                    self.logger.error(fr"Failure of stage : {subcommand}")
                    sys.exit(1)
                            
            if subcommand == "deploy post-data":
                self.logger.info(fr"Begining stage : {subcommand}......")
                if self.dcg_inst.deploy_postdata_cmd() == 0:
                    self.logger.info(fr"Completion of stage : {subcommand}")
                else:
                    self.logger.error(fr"Failure of stage : {subcommand}")
                    sys.exit(1)

            if subcommand == "test-migrator":
                self.logger.info(fr"Begining stage : {subcommand}......")
                if self.dcg_inst.test_migrator_cmd() == 0:
                    self.logger.info(fr"Completion of stage : {subcommand}")
                else:
                    self.logger.error(fr"Failure of stage : {subcommand}")
                    sys.exit(1)