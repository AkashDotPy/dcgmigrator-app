from schema_validation.validation import Validation
from trigger_sanity.trigger_sanity import TestTrigger
from code_sanity.code_sanity import TestCode
from os_operation.ora2pg_commands import ora2pgCommand
from os_operation.os_handling import DirectoryPath
from ora2pg_schema_validator.ora2pg_validation import Ora2pgValidation
from dcgmigrator_core.logging_operation import HandleLogging
from ora2pg_count_validator.count_validation import CountValidation
from ora2pg_view_validator.view_validation import ViewValidation
from database_operation.oracle import OracleDatabaseManagement

class MigratorValidation:

    def __init__(self,project_name):
        self.project_name = project_name
        self.schema_inst = Validation(project_name)
        self.trigger_inst = TestTrigger(project_name)
        self.code_inst = TestCode(project_name)
        self.cmd = ora2pgCommand(project_name)
        self.os_inst = DirectoryPath(project_name)
        self.ora2pg_val_inst = Ora2pgValidation(project_name)
        self.cnt_val_inst = CountValidation(project_name)
        self.view_val_inst = ViewValidation(project_name)
        self.ora_inst = OracleDatabaseManagement(project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def test_migrator(self,t, status="fail",schemalist= None):
        #removing trigger sanity as it is performed during post data deployment
        validationtypes = ["schema","code","ora2pg_validate"]

        if t == None:
            for type in validationtypes:
                if type == "schema":
                    self.logger.info("DCGMigrator schema validation process started.....")
                    self.schema_inst.test_schema(self.project_name)
                    self.logger.info("DCGMigrator schema validation process ends")

                if type == "trigger":
                    self.logger.info("DCGMigrator trigger sanity process started.....")
                    self.trigger_inst.test_trigger_sanity(self.project_name)
                    self.logger.info("DCGMigrator trigger sanity process ends")

                if type == "code":
                    self.logger.info("DCGMigrator code sanity process started.....")
                    self.code_inst.test_code_sanity(self.project_name)
                    self.logger.info("DCGMigrator code sanity process ends")

                if type == "ora2pg_validate":
                    self.logger.info("Ora2pg validation process started.....")
                    self.cmd.test(self.project_name,"test_ora2pg")
                    self.cmd.test_count(self.project_name,"test_count_ora2pg")
                    self.cmd.test_view(self.project_name,"test_view_ora2pg")
                    self.ora2pg_val_inst.ora2pg_schema_validation(status)
                    self.cnt_val_inst.ora2pg_count_generator(self.project_name,status)
                    self.view_val_inst.ora2pg_view_generator(self.project_name,status)
                    self.logger.info("Ora2pg validation process ends")

            self.os_inst.report_zip_file(self.project_name)

        else:
            if t == "schema":
                self.logger.info("DCGMigrator schema validation process started.....")
                self.schema_inst.test_schema(self.project_name)
                self.logger.info("DCGMigrator schema validation process ends")

            if t == "trigger":
                self.logger.info("DCGMigrator trigger sanity process started.....")
                self.trigger_inst.test_trigger_sanity(self.project_name)
                self.logger.info("DCGMigrator trigger sanity process ends")

            if t == "code":
                self.logger.info("DCGMigrator code sanity process started.....")
                if schemalist:
                    self.code_inst.test_code_sanity(self.project_name,schemalist)
                else:
                    self.code_inst.test_code_sanity(self.project_name)
                self.logger.info("DCGMigrator code sanity process ends")

            if t == "test_ora2pg":
                self.cmd.test(self.project_name,t)
                if self.ora2pg_val_inst.ora2pg_schema_validation(status):
                    print("ora2pg schema validation is generated")
                else:
                    print("ora2pg schema validation report was unable to generate")

            if t == "test_count_ora2pg":
                self.cmd.test_count(self.project_name,t)
                if self.cnt_val_inst.ora2pg_count_generator(self.project_name,status):
                    print("ora2pg count validation is generated")
                else:
                    print("ora2pg count validation report was unable to generate")

            if t == "test_view_ora2pg":
                self.cmd.test_view(self.project_name,t)
                if self.view_val_inst.ora2pg_view_generator(self.project_name,status):
                    print("ora2pg view validation is generated")
                else:
                    print("ora2pg view validation is unable to generate")

            if t == "ora2pg_validate":
                self.logger.info("Ora2pg validation process started.....")
                self.cmd.test(self.project_name,"test_ora2pg")
                self.cmd.test_count(self.project_name,"test_count_ora2pg")
                self.cmd.test_view(self.project_name,"test_view_ora2pg")
                self.ora2pg_val_inst.ora2pg_schema_validation(status)
                self.cnt_val_inst.ora2pg_count_generator(self.project_name,status)
                self.view_val_inst.ora2pg_view_generator(self.project_name,status)
                self.logger.info("Ora2pg validation process ends")

        




