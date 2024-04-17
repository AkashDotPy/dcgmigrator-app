from sqlalchemy import create_engine, text
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
from database_operation.postgres import PostgresDatabase
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.logging_operation import HandleLogging
import os

class TestTrigger:
    def __init__(self,project_name):
        self.project_name = project_name
        self.pg_inst = PostgresDatabase(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def db_connection(self,project_name):
        if self.pg_inst.execution_conn(project_name):
            engine,connection,pg_schema = self.pg_inst.execution_conn(project_name)
            return engine,connection,pg_schema
        else:
            return None

    def load_template(self):
        env = Environment(loader=FileSystemLoader('trigger_sanity'))
        template = env.get_template(r'trigger_sanity_template.html')
        return template

    def read_Sanity(self,pg_schema):
        file_name = r"trigger_script.sql"
        dir_path = r"trigger_sanity"
        file_path = self.os_inst.os_join(dir_path,file_name)
        with open(file_path, 'r') as sqlfile:
            query = sqlfile.read()
        Replace_schema_name = query.replace("<<postgres_schema_name>>", pg_schema)
        return Replace_schema_name

    def generate_summary_pie_chart(self,execution_results,pg_schema,project_name):
        if execution_results:
            statuses = [result['status'] for result in execution_results.values()]
            unique_statuses = list(set(statuses))
            colors = ['#4A90E2', '#B9C3F5']
            status_counts = [statuses.count(status) for status in unique_statuses]
            plt.figure(figsize=(8, 8))
            plt.pie(status_counts, labels=unique_statuses, autopct='%1.1f%%', startangle=140,shadow=True,colors=colors,textprops={'fontsize': 16})
            plt.title('Trigger Sanity Execution Summary',fontsize=16)
   
            file_name = f"trigger_summary.png"
            file_path = self.os_inst.trigger_sanity_report_path(project_name,file_name,pg_schema)
            plt.savefig(file_path)
            plt.close()
    
    def execution_sanity(self,engine,Replace_schema_name,connection,template,pg_schema):
        execution_results = {}

        result = connection.execute(text(Replace_schema_name))
        df = pd.DataFrame(result)
        Session = sessionmaker(bind=engine)
        for index, row in df.iterrows():
            session = Session()
            
            result_dict = {  'table_schema': row.iloc[0],  'table_name': row.iloc[1],  'trigger_schema': row.iloc[2],  
            'trigger_name': row.iloc[3],
             'event_manipulation': row.iloc[3],
              'activation': row.iloc[4],
              'status': None
            }


            try:
                session.execute(text(row[6]))
                session.commit()
                result_dict['status'] = 'Success'

            except Exception as e:
                final_execution = f"Error : {e.__cause__}"
                result_dict['Error_reason'] = final_execution
                session.rollback()
                result_dict['status'] = 'Failure'

            finally:
                session.close()
            
            execution_results[f"{row.iloc[1]}_{row.iloc[3]}"] = result_dict

        engine.dispose()

        Rendered_Html = template.render(execution_results=execution_results,pg_schema=pg_schema)
        return Rendered_Html,execution_results

    def html_report(self,Rendered_Html,pg_schema,project_name, runtype):
        file_name = f"trigger_sanity_{pg_schema}.html"
        file_path = self.os_inst.trigger_sanity_report_path(project_name,file_name,pg_schema,runtype)
        with open(file_path, "w") as html_file:
            html_file.write(Rendered_Html)
        
        self.logger.info(f"Trigger sanity report for {pg_schema} is generated \n{file_path}")

    def test_trigger_sanity(self,project_name, runtype = "POST_DATALOAD"):
        if self.db_connection(project_name):
            connection,engine,pg_schema = self.db_connection(project_name)
            Replace_schema_name = self.read_Sanity(pg_schema)
            template = self.load_template()
            Rendered_Html,execution_results =  self.execution_sanity(connection,Replace_schema_name,engine,template,pg_schema)
            self.generate_summary_pie_chart(execution_results,pg_schema,project_name) 
            self.html_report(Rendered_Html,pg_schema,project_name, runtype)        