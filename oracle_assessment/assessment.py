import cx_Oracle
from sqlalchemy import create_engine
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from database_operation.oracle import OracleDatabaseManagement
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.logging_operation import HandleLogging

data = {}
descriptions = {}
title = {}

class OracleAssessment:
   def __init__(self, project_name):
      self.project_name = project_name
      self.ora_inst = OracleDatabaseManagement(self.project_name)
      self.os_inst = DirectoryPath(self.project_name)
      log_instance = HandleLogging(self.project_name)
      self.logger = log_instance.handle_log()

   def load_template(self):
      env = Environment(loader=FileSystemLoader('oracle_assessment'))
      template = env.get_template('template.html')
      return template

   def database_connection(self):
      conn_oracle,ora_schema = self.ora_inst.schema_val_oraconn(self.project_name)
      return conn_oracle,ora_schema

   def read_csv(self):
      dir_path = r"oracle_assessment"
      file_name = r"oracle_csv_file.csv"
      file_path = self.os_inst.os_join(dir_path,file_name)
      # csv_path = r"OracleAssessment\oracle_csv_file.csv"
      csv_data = pd.read_csv(file_path)
      return csv_data

   def execution(self,csv_data,conn_oracle,ora_schema,template):
      for index,row in csv_data.iterrows():
         module = row['module']
         description = row['description']
         sql_query = row['sqlquery']

         replace_query = sql_query.replace("<<ORACLE_SCHEMA>>", ora_schema)
         result = pd.read_sql_query(replace_query,conn_oracle)

         data[index] = result
         descriptions[index] = description
         title[index] = module

      rendered_html = template.render(title=title, descriptions=descriptions, data=data)
      return rendered_html

   def html_report(self,rendered_html):
      file_name = r"oracle_assessment_report.html"
      file_path = self.os_inst.ora_assessment_report_path(self.project_name,file_name)
      with open(file_path,"w") as html_file:
         html_file.write(rendered_html)
         self.logger.info(f"Oracle assessment report generated successfully\nReport : {file_path}")

   def oracle_assessment(self,project_name):
      template = self.load_template()
      conn_oracle,ora_schema = self.database_connection()
      csv_data = self.read_csv()
  
      rendered_html = self.execution(csv_data,conn_oracle,ora_schema,template)
      self.html_report(rendered_html)


