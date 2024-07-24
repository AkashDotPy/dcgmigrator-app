#Test submodule changes to be updated
import argparse,sys
from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_config.config import ConfigInputs
from os_operation.ora2pg_commands import ora2pgCommand
from dcgmigrator_plus.ora2pg_plus import Plus
from dcgmigrator_core.conversion import Convert
from dcgmigrator_core.deployment import deployment
from schema_validation.validation import Validation
from trigger_sanity.trigger_sanity import TestTrigger
from code_sanity.code_sanity import TestCode
from database_operation.oracle import OracleDatabaseManagement
from database_operation.postgres import PostgresDatabase
from dcgmigrator_core.update_status import StatusUpdate
from dcgmigrator_core.logging_operation import HandleLogging
from dcgmigrator_core.prerequisite import ValidatePrerequisite
from dcgmigrator_core.command_flow import CommandFlowManager
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.master_cmd import MasterCommand
from dcgmigrator_core.migrator_validation import MigratorValidation
from oracle_assessment.assessment import OracleAssessment
from code_conversion_matrix.matrix import CodeConversionPlanning 
from dcgmigrator_core.data_transfer import DataTransfer
import os
import time

# define Python user-defined exceptions
class InvalidProjNameException(Exception):
    "Missing Project_Name either in Env Setting or command line argument"
    pass


class ArgumentManagement:

    def arguments():
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="main_command", title="Main Commands")

        # Commands for create-project, create-source, create-target, and show-config
        project_parser = subparsers.add_parser("dcgmigrator", help="AI-powered CLI solution for seamless end-to-end migration to Open Source database")
        project_subparsers = project_parser.add_subparsers(dest="subcommand", title="Subcommands")

        parser_create_project = project_subparsers.add_parser("create-project", help="Create a new Oracle to PostreSQL Migration project")
        parser_create_project.add_argument("--project_name", required=False, help="Mentioned the name of the project")
        parser_create_project.add_argument("--source", required=False,default="Oracle",  help="Source database, currently it is default to Oracle")
        parser_create_project.add_argument("--target", required=False,default="PostgreSQL",  help="Target database, currently it is default to PostgreSQL")

        parser_create_project = project_subparsers.add_parser("remove-project", help="Remove existing Oracle to PostreSQL Migration project")
        parser_create_project.add_argument("--project_name", required=False, help="Mentioned the name of the project")
        parser_create_project.add_argument("--remove_file",action="store_true", required=False , help="Specify if Project files like reports, conversion should be removed for the project")
        parser_create_project.add_argument("--drop_target_schema",action="store_true", required=False , help="Specify if target schema need to be dropped")

        #Removing projects, currenly in backlog as it will romoving all Project related files.
        #parser_create_project = project_subparsers.add_parser("remove-project", help="Remove existing Oracle to PostreSQL Migration project")
        #parser_create_project.add_argument("--project_name", required=False, help="Mentioned the name of the project")
        #parser_create_project.add_argument("--retain_files", required=True,Type=Bool, Default=True, help="control whether project related files need to be deleted.")

        parser_create_source = project_subparsers.add_parser("create-source", help="Add Oracle source details\nprovide oracle source connection details tns alias or (host, port, service name)")
        parser_create_source.add_argument("--project_name", required=False, help="Project name under which source need to be added")
        parser_create_source.add_argument("--ora_user", required=True, help="Specify Oracle user for connection, report execution, and data migration")
        parser_create_source.add_argument("--ora_pwd", required=True, help="Provide Oracle user password")
        parser_create_source.add_argument("--ora_host", required=False, help="Oracle instance hostname or IP address")
        parser_create_source.add_argument("--ora_service_name", required=False, help="Oracle SID or service name")
        parser_create_source.add_argument("--ora_port", required=False, help="Oracle port number")
        parser_create_source.add_argument("--tns_connection", required=False, help="Specify TNS connection.")
        parser_create_source.add_argument("--ora_home", required=False, help="Oracle Home path; by default, it will use the value of the ORACLE_HOME environment variable")
        parser_create_source.add_argument("--ora_schema", required=True, help="Specify Oracle schema to be migrated.")
        
        parser_create_target = project_subparsers.add_parser("create-target", help="Add PostgreSQL DB Target details")
        parser_create_target.add_argument("--project_name", required=False, help="Migration Project name")
        parser_create_target.add_argument("--pg_dbname", required=True, help="PostgreSQL database name")
        parser_create_target.add_argument("--pg_host", required=True, help="PostgreSQL host name")
        parser_create_target.add_argument("--pg_port", required=True, help="PostgreSQL database port")
        parser_create_target.add_argument("--pg_user", required=True, help="PostgreSQL user name, should be same as Oracle Schema to migrate.")
        parser_create_target.add_argument("--pg_password", required=True, help="PostgreSQL master user name password")
        parser_create_target.add_argument("--pg_version", required=True, default="16",  help="Target PostgreSQL Version, Default is 16")


        # Commands for show config details
        parser_show_config = project_subparsers.add_parser("show-config", help="Show Ora2pg config stored")
        parser_show_config.add_argument("--project_name", required=False, help="Project Name to view the configuration")
        
        # Commands to generate config details in ora2pg files.
        parser_show_config = project_subparsers.add_parser("generate-config", help="Generate Ora2pg config information without credentials for local testing")
        parser_show_config.add_argument("--project_name", required=False, help="Project Name to view the configuration")

        # Command for project list
        parser_list_project = project_subparsers.add_parser("list-project", help="List all existing project in DCGMigrator")
        parser_list_project.add_argument("--project_name", required=False, help="Insert the name of the project")
        
        # Commands for update config details
        parser_upd_config = project_subparsers.add_parser("upsert-config", help="Upsert new Ora2pg related config information")
        parser_upd_config.add_argument("--project_name", required=False, help="Insert the name of the project")
        parser_upd_config.add_argument("--key", required=True, help="Ora2pg configuration name")
        parser_upd_config.add_argument("--value", required=True, help="Ora2pg configuration value")

        parser_remv_config = project_subparsers.add_parser("remove-config", help="Remove Ora2pg config from migration projects")
        parser_remv_config.add_argument("--project_name", required=False, help="Insert the name of the project")
        parser_remv_config.add_argument("--key", required=True, help="Ora2pg configuration name")

        # Command for validation of prerequisite
        parser_upd_config = project_subparsers.add_parser("test-prerequisite", help="Validation minimal pre-requistics needed for conversion and data movement.It include checking Ora2pg, psql , Oracle and PostgreSQL connections")
        parser_upd_config.add_argument("--project_name", required=False, help="Insert the name of the project")

        # Command for Oracle assessment
        parser_ora_assess = project_subparsers.add_parser("discovery", help="Oracle asessment and coversion planning report")
        parser_ora_assess.add_argument("--type", required=False, help="Support type as assess or code_planning as two options.If type is ignored, default week will be 10")
        parser_ora_assess.add_argument("--week", required=False,  help="Create code conversion planning as per no.of Weeks specified.")
        parser_ora_assess.add_argument("--project_name", required=False, help="Insert the name of the project")

        # Command for Oracle data type mapping
        parser_data_type = project_subparsers.add_parser("datatypemapping", help="Run data type mapping based on sampling for optimal type in PostgreSQL")
        parser_data_type.add_argument("--project_name", required=False, help="Insert the name of the project")
        parser_data_type.add_argument("--run_only_constraint",action="store_true", required=False, help="Control running data type mapping only for constraint columns")
        parser_data_type.add_argument("--oracle_only_top_n_table", default=10000, required=False, help="Fix no.of Top Tabl as size to run")


        # Commands for converting table
        parser_convert = project_subparsers.add_parser("convert", help="Perform Conversion of Oracle schema and procedural code")
        parser_convert.add_argument("--type", required=False, help="If specify, will convert only specific Database Object Type")
        parser_convert.add_argument("--project_name", required=False, help="Insert the name of the project")
        parser_convert.add_argument("--rundatatypemapping",action="store_true", required=False , help="Control running data type mapping as part of conversion")

        # Commands for deploy data structure
        parser_deploy = project_subparsers.add_parser("deploy", help="Deploy converted Oracle object to target database")
        parser_deploy.add_argument("--type", required=True, help="Support pre-data and post-data, automatically choose object to deploy base on type specified.      ")
        parser_deploy.add_argument("--ON_ERROR_STOP", required=False, type = int,default=0 , help="Enable psql command line ON_ERROR_STOP with 0 or 1")
        parser_deploy.add_argument("--project_name", required=False, help="Migration project name")
        parser_deploy.add_argument("--continue_deployment", required=False,type = bool , default=True, help="Control overall deployment of objects, Default (True")

        # copy data
        parser_copy = project_subparsers.add_parser("copy", help="Migrate data from Oracle to PostgreSQL")
        parser_copy.add_argument("--project_name", required=False, help="Insert the name of the project")
        parser_copy.add_argument("--multiprocess", action="store_true", required=False, help="multiprocess data transfer")
        parser_copy.add_argument("--use_oracle_fdw", required=False, default=False, help="perfom faster data load using Oracle FDW configured in PostgreSQL")
        parser_copy.add_argument("--continue_on_error", required=False, default=True, help="Continue data load even in case of some failures")
        parser_copy.add_argument("--data_limit", required=False, type=int, help="Limit no.of of rows to migrate, can be use for initial testing")


        # Test data
        parser_test = project_subparsers.add_parser("validate", help="Validate migration for schema, code, and data. Utilize the DCG_REPORT_PATH environment variable to override the default path for the migration report output.")
        parser_test.add_argument("--type", required=False, help='mention validation type, it can be specified as (schema,code(sanity),trigger(sanity),\n ora2pg_validate(run all schema , Data) , ora2pg_schema ,ora2pg_count ,ora2pg_view_count')
        parser_test.add_argument("--validation_error", required=False,type=int,default=10, help='mention validation type, it can be specified as (schema,code(sanity),trigger(sanity),\n ora2pg_validate(run all schema , Data) , ora2pg_schema ,ora2pg_count ,ora2pg_view_count')
        parser_test.add_argument("--schemalist", required=False, help='Mentioned list of schema comma separared to run Code Sanity, added it for Oracle Packages converted as schema in PostgreSQL')
        parser_test.add_argument("--status", required=False, default="Fail", help="Applicable for Ora2pg schema\count\view validation with status as : (Pass\Fail\Both)")
        parser_test.add_argument("--project_name", required=False, help="Migration project name")

        # Commands for source-metadata
        parser_test = project_subparsers.add_parser("source-metadata", help="source metadata of ora2pg")
        parser_test.add_argument("--project_name", required=False, help="Migration project name")
        parser_test.add_argument("--type", required=True, help="support same as Ora2pg (show-table, show-schema, show-version, show-column)")

        #Master command for migration
        parser_test = project_subparsers.add_parser("migrate", help="automate overall migration process")
        parser_test.add_argument("--project_name", required=False, help="Project name")

        return parser.parse_args()

    if __name__ == "__main__":
        args = arguments()
    
        if args.main_command =="dcgmigrator" and args.subcommand !="list-project":
            if args.project_name == None:
                try:
                    if os.environ.get('PROJECT_NAME') == None:
                        raise InvalidProjNameException
                    else:
                        project_name = os.environ.get('PROJECT_NAME')
                except InvalidProjNameException:
                    print("Missing project_name either in Env Setting($PROJECT_NAME) or command line(--project_name) argument")
                    sys.exit(-1)
            else:
                project_name = args.project_name
        else:
            project_name = args.project_name
               
        cmd = ora2pgCommand(project_name)
        config_instance = ConfigInputs(project_name)
        sqlite_instance = SqliteDatabaseManagement(project_name)
        plus_instance = Plus(project_name)
        conv_instance = Convert(project_name)
        deploy_inst = deployment(project_name)
        schema_inst = Validation(project_name)
        trigger_inst = TestTrigger(project_name)
        code_inst = TestCode(project_name)
        ora_inst = OracleDatabaseManagement(project_name)
        status_inst = StatusUpdate(project_name)
        prerec_inst = ValidatePrerequisite(project_name)
        log_inst = HandleLogging(project_name)
        logger = log_inst.handle_log()
        cmd_flow_inst = CommandFlowManager(project_name)
        os_inst = DirectoryPath(project_name)
        ms_cmd_inst = MasterCommand(project_name)
        val_inst = MigratorValidation(project_name)
        assess_inst = OracleAssessment(project_name)
        code_conv_inst = CodeConversionPlanning(project_name)
        pg_inst = PostgresDatabase(project_name)
        data_transfer_inst = DataTransfer(project_name)
        if args.main_command == "dcgmigrator":
            if args.subcommand == "create-project":
                if sqlite_instance.create_project(project_name, args.source, args.target):
                    config_instance.default_config(project_name)
                    status_inst.update_status(args.subcommand,project_name)

            if args.subcommand == "remove-project":
                #changed with confirmation
                if sqlite_instance.validate_project(project_name):
                    removemsg = f"Please cofirm, if you want to remove project - {project_name.upper()}"
                    confirm = input("%s (y/N) ?" % removemsg).lower() in ('y','yes')
                    if confirm:
                        if args.remove_file and os_inst.remove_project_dir(project_name):
                            logger.info(f"Project name - {project_name} related all generated files are remove")
                        if args.drop_target_schema and pg_inst.postgres_drop_schema(project_name):
                            logger.info(f"Project name - {project_name} target schema is dropped")
                        sqlite_instance.remove_project(project_name)
                else:
                    logger.error(f"Migration Project name - {project_name} does not exists, skipping remove-project")

            if args.subcommand == "list-project":
                sqlite_instance.fetch_project(project_name)

            if args.subcommand == "create-source":
                if sqlite_instance.validate_project(project_name) and cmd_flow_inst.command_manager(args.subcommand,project_name):
                    if args.tns_connection:
                        if config_instance.oracle_cred(project_name,args.ora_home,args.ora_user,args.ora_pwd,args.tns_connection,args.ora_schema):
                            status_inst.update_status(args.subcommand,project_name)
                            print(f"Oracle Source added successfully for Project - {project_name}")
                        else:
                            print(f"Oracle Source addition failed for Project - {project_name}")

                    elif args.ora_host and args.ora_service_name and args.ora_port:
                        if config_instance.local_oracle_cred(project_name,args.ora_home,args.ora_host,args.ora_service_name,args.ora_port,args.ora_user,args.ora_pwd,args.ora_schema):
                            status_inst.update_status(args.subcommand,project_name)
                            print(f"Oracle Source added successfully for Project - {project_name}")
                        else:
                            print(f"Oracle Source addition failed for Project - {project_name}")
                    else:
                        print("Please provide oracle source connection details tns alias or (host, port, service name)")
  
                else:
                    logger.error(f"Project name - {project_name} is not created, please use create-project option first")
                    
            if args.subcommand == "create-target":
                if not sqlite_instance.validate_project(project_name):
                    logger.error(f"Project name - {project_name} is not created, please use create-project option")
                elif  sqlite_instance.fetch_config_value(project_name,'ORA_SCHEMA').lower() != args.pg_user.lower():
                    oracleschema = sqlite_instance.fetch_config_value(project_name,'ORA_SCHEMA').lower()
                    logger.error(f"PostgreSQL user name - {project_name} is not equal to migrating oracle schema - {oracleschema.upper()} , please use correct mapping i.e. Oracle Schema = Target User")
                elif sqlite_instance.validate_project(project_name) and sqlite_instance.fetch_config_value(project_name,'ORA_SCHEMA').lower() == args.pg_user.lower() and cmd_flow_inst.command_manager(args.subcommand,project_name):
                    config_instance.pg_cred(project_name,args.pg_dbname,args.pg_host,args.pg_port,args.pg_user,args.pg_password,args.pg_version)
                    print(f"PostgreSQL Source added successfully for Project - {project_name}")
                    status_inst.update_status(args.subcommand,project_name)
                else:
                    logger.error(f"Issue was target creation.")

            if args.subcommand == "show-config":
                if not sqlite_instance.show_config(project_name):
                    logger.error(f"Migration project is not created or unable to fetch config : {project_name}")

            if args.subcommand == "generate-config":
                if sqlite_instance.validate_project(project_name):
                    config_instance.refresh_ora2pg_config_withoutpasswd(project_name)

            if args.subcommand == "upsert-config":
                if sqlite_instance.validate_project(project_name):
                    sqlite_instance.update_config(args.key, args.value, project_name)

            if args.subcommand == "remove-config":
                if sqlite_instance.validate_project(project_name):
                    removeconf = f"Please cofirm, if you want to remove config - {project_name.upper()}"
                    input_val = input("%s (Y/N) ?" % removeconf).lower() in ('y','yes')
                    if input_val:
                        sqlite_instance.remove_config(project_name,args.key)
                else:
                    logger.error(f"Migration Project name - {project_name} does not exists, skipping remove-config")

            if args.subcommand == "test-prerequisite":
                # if cmd_flow_inst.command_manager(args.subcommand,project_name):
                    status_inst.pre_check_status(args.subcommand,project_name)

            if args.subcommand == "discovery":
                if sqlite_instance.validate_project(project_name):
                    if args.type == "assess":
                        assess_inst.oracle_assessment(project_name)
                    elif args.type == "code_planning" and args.week is not None:
                        code_conv_inst.code_conv_planning(project_name,args.week)
                    elif args.type == None and args.week is not None:
                        assess_inst.oracle_assessment(project_name)
                        code_conv_inst.code_conv_planning(project_name,args.week)
                    elif args.type == "code_planning" and args.week is None:
                        print("Please provide no.of week input for Code Planning, currently missing information")
                        print("Sample command dcgmigrator discovery --type code_planning --week 5")
                    else:
                        print("Please check discovery help currently missing information based on type")

                else:
                    logger.error(f"Project name - {project_name} is not created, please use create-project option first")

            if args.subcommand == "convert":
                if sqlite_instance.validate_project(project_name):
                    if cmd_flow_inst.command_manager(args.subcommand,project_name):
                        conv_instance.convert(project_name, args.type,args.rundatatypemapping)  
                        status_inst.update_status(args.subcommand,project_name)
                else:
                    logger.error(f"Project name - {project_name} is not created, please use create-project option first")

            if args.subcommand == "datatypemapping":
                if sqlite_instance.validate_project(project_name):
                    if plus_instance.modify_type(project_name,args.run_only_constraint, args.oracle_only_top_n_table):
                        logger.info(f"Data type mapping completed for Project - {project_name}")
                    else:
                        logger.error(f"Data type failed for Project - {project_name}")
                else:
                    logger.error(f"Project name - {project_name} is not created, please use create-project option first")

            if args.subcommand == "deploy":
                if sqlite_instance.validate_project(project_name):
                    if args.type == "pre-data":
                        if cmd_flow_inst.command_manager(args.subcommand +" "+ args.type,project_name):
                                deploy_inst.pre_data_deployment(args.ON_ERROR_STOP,project_name , args.continue_deployment)
                                status_inst.update_status(args.subcommand +" "+ args.type,project_name)
                    elif args.type == "post-data":
                        if cmd_flow_inst.command_manager(args.subcommand +" "+ args.type,project_name):
                                deploy_inst.post_data_deployment(args.ON_ERROR_STOP,project_name, args.continue_deployment)
                                status_inst.update_status(args.subcommand +" "+ args.type,project_name)
                    else:
                        logger.error(f"Incorrect argument type  - {args.type}, it can be pre-data/post-data")

                else:
                    logger.error(f"Project name - {project_name} is not created, please use create-project option first")

            if args.subcommand == "copy":
                # if cmd_flow_inst.command_manager(args.subcommand,project_name):
                    start = time.time()
                    if args.multiprocess:
                        if data_transfer_inst.multiprocess_copy(project_name,args.use_oracle_fdw, args.continue_on_error, args.data_limit):
                            status_inst.update_status(args.subcommand,project_name)
                    else:
                        if cmd.copy_data_movement(project_name,args.use_oracle_fdw, args.continue_on_error, args.data_limit):
                            status_inst.update_status(args.subcommand,project_name)
                    end = time.time()
                    time_taken = end - start
                    print(f"Total Time for Data Migration was {time_taken : .2f} seconds")

            if args.subcommand == "validate":
                if sqlite_instance.validate_project(project_name):
                    if not args.schemalist:
                        val_inst.test_migrator(args.type,args.validation_error,args.status)
                        status_inst.update_status(args.subcommand,project_name)
                    else:
                        val_inst.test_migrator(args.type,args.validation_error, args.status,args.schemalist)
                        status_inst.update_status(args.subcommand,project_name)
                else:
                    logger.error(f"Project name - {project_name} is not created, please use create-project option first")


            if args.subcommand =="migrate":
                 ms_cmd_inst.master_cmd(project_name)

            if args.subcommand == "source-metadata":
                if args.type == "show-table":
                    cmd.show_table(project_name)

                if args.type == "show-column":
                    cmd.show_column(project_name)

                if args.type == "show-version":
                    cmd.show_version(project_name)

                if args.type == "show-schema":
                    cmd.show_schema(project_name)
                     
            
                
            
            
            


