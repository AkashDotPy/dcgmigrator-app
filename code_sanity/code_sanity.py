from sqlalchemy import create_engine, text
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
from database_operation.postgres import PostgresDatabase
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.logging_operation import HandleLogging
from database_operation.oracle import OracleDatabaseManagement
import os

class TestCode:
    def __init__(self,project_name):
        self.project_name = project_name
        self.pg_inst = PostgresDatabase(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        self.ora_inst = OracleDatabaseManagement(project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def db_connection(self,project_name):
        if self.pg_inst.execution_conn(project_name):
            engine,connection,pg_schema = self.pg_inst.execution_conn(project_name)
            return connection,engine,pg_schema
        else:
            None

    def load_template(self):
        env = Environment(loader=FileSystemLoader('code_sanity'))
        template = env.get_template(r'code_sanity_template.html')
        return template

    def read_sql_script(self,pg_schema):
        dir_path = r"code_sanity"
        file_name = r"code_script.sql"
        file_path = self.os_inst.os_join(dir_path,file_name)
        with open(file_path, 'r') as sqlfile:
            query = sqlfile.read()
        Replace_schema_name = query.replace("<<postgres_schema_name>>",pg_schema)
        return Replace_schema_name

    def generate_summary_pie_chart(self,execution_results,pg_schema,project_name):
        if execution_results:
            statuses = [result['status'] for result in execution_results.values()]
            unique_statuses = list(set(statuses))
            colors = ['#4A90E2', '#B9C3F5']
            status_counts = [statuses.count(status) for status in unique_statuses]
            # plt.rcParams.update({'font.size': 18})
            plt.figure(figsize=(8, 8))
            plt.pie(status_counts, labels=unique_statuses, autopct='%1.1f%%', startangle=140,shadow=True, colors=colors,textprops={'fontsize': 16})
            plt.title('Code Sanity Execution Summary',fontsize=16)
            file_name = f"code_summary.png"
            file_path = self.os_inst.code_sanity_report_path(self.project_name,file_name,pg_schema)
            plt.savefig(file_path)
            plt.close()

    def execution_sanity(self,connection,Replace_schema_name,engine,template,pg_schema):
        execution_results = {}
        Session = sessionmaker(bind=engine)

        result = connection.execute(text(Replace_schema_name))
        df = pd.DataFrame(result)

        for index, row in df.iterrows():
            session = Session()
            result_dict = { 
                'routine_name': row.iloc[0],
                'routine_type': row.iloc[1],
                'specific_schema': row.iloc[2],
                'status': None,
                }    
            try:
                session.execute(text(row.iloc[3]))
                session.rollback()
                result_dict['status'] = 'Success'

            except Exception as e:
                final_execution = f"Error : {e.__cause__}"
                result_dict['Error_reason'] = final_execution
                session.rollback()
                result_dict['status'] = 'Failure'

            finally:
                session.close()

            execution_results[f"{row.iloc[0]}_{row.iloc[1]}"] = result_dict

        Rendered_Html = template.render(execution_results=execution_results,pg_schema=pg_schema)
        return Rendered_Html,execution_results

    def html_report(self,Rendered_Html,pg_schema,project_name):
        file_name = f"code_mocksanity_{pg_schema}.html"
        file_path = self.os_inst.code_sanity_report_path(self.project_name,file_name,pg_schema)
        with open(file_path, "w") as html_file:
            html_file.write(Rendered_Html)

        self.logger.info(f"Code sanity report for {pg_schema} is generated at below path \n{file_path}")
        

    def test_code_sanity(self,project_name,schemalist=None):
        if self.db_connection(project_name):
   
            connection,engine,pg_schema = self.db_connection(project_name)
            if schemalist != None:
                for schema in schemalist.split(","):                
                    if  self.pg_inst.postgres_schema_check(self.project_name, schema) and (self.ora_inst.validate_oracle_schema(self.project_name, schema) or self.ora_inst.oracle_package_exists(self.project_name, schema)):
                        pg_schema = schema
                        Replace_schema_name = self.read_sql_script(pg_schema)
                        template = self.load_template()
                        Rendered_Html,execution_results =  self.execution_sanity(connection,Replace_schema_name,engine,template,pg_schema)
                        self.generate_summary_pie_chart(execution_results,pg_schema,project_name) 
                        self.html_report(Rendered_Html,pg_schema,project_name) 
                    else:
                        self.logger.error(f"Input schema is either missing in Oracle or Migrated PostgreSQL database")
            else:
                Replace_schema_name = self.read_sql_script(pg_schema)
                template = self.load_template()
                Rendered_Html,execution_results =  self.execution_sanity(connection,Replace_schema_name,engine,template,pg_schema)
                self.generate_summary_pie_chart(execution_results,pg_schema,project_name) 
                self.html_report(Rendered_Html,pg_schema,project_name) 

