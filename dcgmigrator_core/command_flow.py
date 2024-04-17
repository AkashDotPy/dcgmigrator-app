from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_core.logging_operation import HandleLogging



class CommandFlowManager:

    def __init__(self,project_name):
        self.project_name = project_name
        self.sqlite_inst = SqliteDatabaseManagement(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def command_order(self):
        stage = {
                "create-project"       : "initialized_project",
                "create-source"        : "initialized_source",
                "create-target"        : "initialized_target",
                "test-prerequisite"    : "pre-check pass",
                "convert"              : "converted", 
                "convert table"        : "converted", 
                "deploy pre-data"      : "deployed-pre-data",
                "copy"                 : "data transfer",
                "deploy post-data"     : "deployed-post-data",
                "test-migrator"        : "validated"
                }
        order = {
                "initialized_project"  : 1,
                "initialized_source"   : 2,
                "initialized_target"   : 3,
                "pre-check pass"       : 4,
                "converted"            : 5,
                "deployed-pre-data"    : 6,
                "data transfer"        : 7,
                "deployed-post-data"   : 8,
                "validated"            : 9
                }
        return stage,order
    
    def validate_flow(self,subcommand,stage,order,project_name):
        try:
            status = self.sqlite_inst.fetch_status(project_name)

            order_key = list(order.keys())
            order_value = list(order.values())

            stage_key = list(stage.keys())
            stage_value = list(stage.values())

            current_status_no = order_value[order_key.index(status)]
            current_cmd = stage_key[stage_value.index(status)]
            subcommand_stat = stage_value[stage_key.index(subcommand)]
            given_stage = stage_key[stage_value.index(subcommand_stat)]
            subcommand_stat_no = order_value[order_key.index(subcommand_stat)]

            if subcommand_stat_no !=  current_status_no and subcommand_stat_no > current_status_no:
                next_stat = order_key[order_value.index(current_status_no + 1)]
                next_cmd = stage_key[stage_value.index(next_stat)]

                if status in order_key:
                
                    if subcommand in stage_key:

                        if subcommand_stat in order_key:

                            if subcommand_stat_no > current_status_no + 1:
                                if current_status_no + 1 in order_value:
                                    self.logger.error(f"you are at : {current_cmd} stage \n your further stage should be : {next_cmd}")
                                else:
                                    self.logger.error("You have already completed all the stages")
                                return False
                            elif subcommand_stat_no < current_status_no:
                                if current_status_no + 1 in order_value:
                                    self.logger.error(f"you have already completed stage : {given_stage}  \n you are at stage : {current_cmd} \n your further stage should be : {next_cmd}")
                                else:
                                    self.logger.error("You have already completed all the stages")
                                    return False
                            elif subcommand_stat_no == current_status_no:
                                self.logger.error(f"you have already complete stage : {given_stage} \n please move to further stage : {next_cmd}")
                                return False

                            elif subcommand_stat_no +1 > current_status_no:
                                return True

                else:
                    self.logger.error("You have to begin with stage : create-project first")
                    return False



            elif subcommand_stat_no == 10:
                self.logger.error(f"you have already complete stage : {given_stage}")
                return False

            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def command_manager(self,subcommand,project_name):
        stage,order = self.command_order()
        status = self.sqlite_inst.fetch_status(project_name)

        if status == "pre-check fail":
            self.logger.error(f"Precheck of migration pre-requistics failed : Current Status -  {status}")
            return False

        if self.validate_flow(subcommand,stage,order,project_name):
            return True
        else:
            self.logger.error(f"Precheck for migration failed ")
            return False

                

