import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from os_operation.os_handling import DirectoryPath
from database_operation.sqlite import SqliteDatabaseManagement
from dcgmigrator_core.logging_operation import HandleLogging

class ViewValidation:

    def __init__(self,project_name):
        self.os_inst = DirectoryPath(project_name)
        log_instance = HandleLogging(project_name)
        self.sqlite_inst = SqliteDatabaseManagement(project_name)
        self.logger = log_instance.handle_log()

    def load_template(self):
        env = Environment(loader=FileSystemLoader('ora2pg_view_validator'))
        template = env.get_template("template.html")
        return template

    def status_control(self, merged_df, input_status):
        if input_status != None:
            if input_status.lower() == 'pass':
                data_df = merged_df[merged_df['Status'] == "Pass"]
            elif input_status.lower() == 'fail':
                data_df = merged_df[merged_df['Status'] == "Fail"] 
            elif input_status.lower() == 'both':
                data_df = merged_df
        else:
            data_df = merged_df[merged_df['Status'] == "Fail"]
        return data_df

    def _ora2pg_view_generator(self,template,project_name,input_status):
        input_file_name = r"test_view_ora2pg.txt"
        input_dir_path = self.os_inst.ora2pg_test_report(project_name)
        input_file_path = self.os_inst.os_join(input_dir_path,input_file_name)
        output_file_name = r"ora2pg_view_validation.csv"
        out_dir_path = self.os_inst.dcg_ora_validation_report_path(project_name,output_file_name)
        output_html_file_name = r"ora2pg_view.html"
        out_dir_path = self.os_inst.dcg_ora_validation_report_path(project_name,output_file_name)
        html_dir_path = self.os_inst.dcg_ora_validation_report_path(project_name,output_html_file_name)
        schema = self.sqlite_inst.fetch_config_value(project_name,"PG_SCHEMA")

        df = pd.read_csv(input_file_path, sep=":",names=["Database", "Oracle_Table", "Count", "Dummy"]) 

        if len(df) > 1:
            df.loc[df["Database"] == "ORACLEDB", "Oracle_Table"] = df.loc[df["Database"] == "ORACLEDB","Oracle_Table"].str.lower()
            df.loc[df["Database"] == "POSTGRES", "Oracle_Table"] = df.loc[df["Database"] == "POSTGRES","Oracle_Table"].str.split(".").str[1]
            df = df.loc[:, ~df.columns.isin(["Dummy"])]
            oracle = df[df["Database"] == "ORACLEDB"]
            postgres = df[df["Database"] == "POSTGRES"]
            merged_df = oracle.merge(postgres, on ="Oracle_Table", sort = True, how ="left", indicator  ="ref", suffixes=("_oracle", "_postgres"))
            merged_df = merged_df.loc[:, ~merged_df.columns.isin(["ref"])]
            merged_df = merged_df.loc[:, ~merged_df.columns.isin(["Database_oracle"])]
            merged_df = merged_df.loc[:, ~merged_df.columns.isin(["Database_postgres"])]
            merged_df = merged_df.loc[:, ~merged_df.columns.isin(["Dummy"])]
            merged_df["Status"] = ""
            merged_df["Difference (percentage)"] = ""
            merged_df["Count_oracle"] = pd.to_numeric(merged_df["Count_oracle"]).fillna(0) .astype(int)
            merged_df["Count_postgres"] = pd.to_numeric(merged_df["Count_postgres"]).fillna(0).astype(int)
            merged_df['Status'] = np.where(merged_df['Count_oracle'].to_numpy() == merged_df    ['Count_postgres'].to_numpy(),'Pass','Fail')
            np.seterr(divide='ignore', invalid='ignore')
            count_ora = merged_df['Count_oracle'].to_numpy()
            count_pg = merged_df['Count_postgres'].to_numpy()
            merged_df['Difference (percentage)'] = np.where((count_ora != 0),np.round((count_ora -  count_pg)/count_ora * 100, 2),0)
            data_df = self.status_control(merged_df, input_status)

            if len(data_df.index) != 0:
                rendered_html = template.render(merged_df=data_df,schema=schema)
                with open(html_dir_path, "w") as html_file:
                    html_file.write(rendered_html)
                data_df.to_csv(out_dir_path, index = False)
                self.status_pie_chart(project_name,data_df)
                return True
            else:
                self.logger.error(f"No Failed data present for ora2pg table data")                
                return False
            
    def status_pie_chart(self,project_name,merged_df):
        if len(merged_df.index) != 0:
            count = merged_df['Status'].value_counts()
            count_pass = count.get('Pass', 0)
            count_fail = count.get('Fail', 0)
            colors = ['#4A90E2', '#B9C3F5']
            plt.pie([count_pass, count_fail],  colors=colors,labels=['Pass', 'Fail'], autopct=lambda p: f'{int(p * sum([count_pass,count_fail]) / 100)}',   startangle=90)
            plt.axis('equal')
            plt.title('Ora2pg view validation summary')
            file_name = r"view_status.png"
            out_dir_path = self.os_inst.dcg_ora_validation_report_path(project_name,file_name)
            plt.savefig(out_dir_path, format='png')
            plt.close()
    
    def ora2pg_view_generator(self,project_name,input_status):
        template = self.load_template()
        if self._ora2pg_view_generator(template,project_name,input_status):
            return True
        else:
            return False