import pandas as pd
import argparse
from jinja2 import Environment, FileSystemLoader
from matplotlib import pyplot as plt
import numpy as np
import sys
import os
from os_operation.os_handling import DirectoryPath

data_dict = {}
summary_dict = {}
description = {}
content_index = {}
difference = {}

class Ora2pgValidation:
    def __init__(self, project_name):
        self.project_name = project_name
        self.os_inst = DirectoryPath(self.project_name)

    def load_template(self):
        env = Environment(loader=FileSystemLoader('ora2pg_schema_validator'))
        template = env.get_template("template.html")
        return template
    
    def status_control(self, df, input_status):
        if input_status != None:
            if input_status.lower() == 'pass':
                data_df = df[df['Status'] == "Pass"]
            elif input_status.lower() == 'fail':
                data_df = df[df['Status'] == "Fail"] 
            elif input_status.lower() == 'both':
                data_df = df[df['Status'] == "Both"] 
            else:
                data_df = df[df['Status'] == "Fail"]
        else:
            data_df = df[df['Status'] == "Fail"]

        return data_df

    def execution(self, input_status):
        summary = pd.DataFrame(columns=["Oracle_Table", "Count_oracle", "Count_postgres", "Status", "Difference (percentage)"])
        schema =""
        input_file_name = r"test_ora2pg.txt"
        input_dir_path = self.os_inst.ora2pg_test_report(self.project_name)
        input_file_path = self.os_inst.os_join(input_dir_path,input_file_name)

        try:
            if not os.path.exists(input_file_path):
                print(f"Incorrect Path or file does not exists")
                sys.exit(1)
            with open(input_file_path, 'r' , encoding='utf-8') as file:
                file_content = file.read()

        except Exception as e:
            print(f"Incorrect Path or file does not exists -  {e}")
            sys.exit(1)


        sections = {'[TEST COLUMNS COUNT]'              :'[ERRORS COLUMNS COUNT]',
                    '[TEST INDEXES COUNT]'              :'[ERRORS INDEXES COUNT]',
                    '[TEST UNIQUE CONSTRAINTS COUNT]'   :'[ERRORS UNIQUE CONSTRAINTS COUNT]',
                    '[TEST PRIMARY KEYS COUNT]'         :'[ERRORS PRIMARY KEYS COUNT]',
                    '[TEST CHECK CONSTRAINTS COUNT]'    :'[ERRORS CHECK CONSTRAINTS COUNT]',
                    '[TEST NOT NULL CONSTRAINTS COUNT]' :'[ERRORS NOT NULL CONSTRAINTS COUNT]',
                    '[TEST COLUMN DEFAULT VALUE COUNT]' :'[ERRORS COLUMN DEFAULT VALUE COUNT]',
                    '[TEST FOREIGN KEYS COUNT]'         :'[ERRORS FOREIGN KEYS COUNT]',
                    '[TEST PARTITION COUNT]'            :'[ERRORS PARTITION COUNT]',
                    '[TEST TABLE COUNT]'                :'[ERRORS TABLE COUNT]',
                    '[TEST TABLE TRIGGERS COUNT]'       :'[ERRORS TABLE TRIGGERS COUNT]',
                    '[TEST TRIGGER COUNT]'              :'[ERRORS TRIGGER COUNT]',
                    '[TEST VIEW COUNT]'                 :'[ERRORS VIEW COUNT]',
                    '[TEST MVIEW COUNT]'                :'[ERRORS MVIEW COUNT]',
                    '[TEST SEQUENCE COUNT]'             :'[ERRORS SEQUENCE COUNT]',
                    '[TEST TYPE COUNT]'                 :'[ERRORS TYPE COUNT]',
                    '[TEST FDW COUNT]'                  :'[ERRORS FDW COUNT]',
                    '[TEST FUNCTION COUNT]'             :'[ERRORS FUNCTION COUNT]',
                    '[TEST SEQUENCE VALUES]'            :'[ERRORS SEQUENCE VALUES COUNT]',
                    'DIFF: Function'                   :'is missing in PostgreSQL database.'}

        objects = [ "[TEST TABLE COUNT]","[TEST PARTITION COUNT]", "[TEST TRIGGER COUNT]",
                    "[TEST VIEW COUNT]", "[TEST MVIEW COUNT]", "[TEST SEQUENCE COUNT]",
                    "[TEST TYPE COUNT]", "[TEST FDW COUNT]", "[TEST FUNCTION COUNT]"]

        for key, value in sections.items():
            content = False
            df = pd.DataFrame(columns=["Database", "Oracle_Table", "Count"])
            for item in file_content.splitlines():
                data = item.strip()
                if data == key:
                    content = True
                    continue
                if data == value:
                    break
                if content:
                    line = data.split(":")
                    if schema == "" and "ORACLEDB" not in line: 
                        schema = line[1].split(".")[0]
                    df.loc[len(df)] = line
                if key and value in data:
                    ndata = data.split()[2]
                    schema_name = ndata.split('.')[0]
                    function_name = ndata.split('.')[1]

                    if schema_name in difference:
                        if function_name not in difference[schema_name]['functions']:
                            difference[schema_name]['count']+=1
                            difference[schema_name]['functions'].append(function_name)
                    else:
                        difference[schema_name] = {'package': schema_name, 'count': 1, 'functions': [function_name]}

            count_1 = df.loc[df["Database"] == "ORACLEDB", "Oracle_Table"].str.split().str.len()
            count_2 = df.loc[df["Database"] == "POSTGRES", "Oracle_Table"].str.split(".").str.len()

            if count_1.eq(1).any():
                df.loc[df["Database"] == "ORACLEDB", "Oracle_Table"] = df.loc[df["Database"] =="ORACLEDB", "Oracle_Table"].str.lower()
            if count_2.eq(2).any():
                df.loc[df["Database"] == "POSTGRES", "Oracle_Table"] = df.loc[df["Database"] =="POSTGRES", "Oracle_Table"].str.split(".").str[1].str.lower()
            else:
                df["Database"] = df["Database"].str.strip()
                df["Oracle_Table"] = df["Oracle_Table"].str.lower()

            oracle = df[df["Database"] == "ORACLEDB"]
            postgres = df[df["Database"] == "POSTGRES"]

            merged_df = oracle.merge(postgres, on ="Oracle_Table", sort = True, how ="left", indicator ="ref", suffixes=("_oracle", "_postgres"))

            merged_df = merged_df.loc[:, ~merged_df.columns.isin(["ref", "Database_oracle", "Database_postgres"])]

            merged_df["Status"] = ""
            merged_df["Difference (percentage)"] = ""

            merged_df["Count_oracle"] = pd.to_numeric(merged_df["Count_oracle"]).fillna(0) .astype(int)
            merged_df["Count_postgres"] = pd.to_numeric(merged_df["Count_postgres"]).fillna(0).astype(int)
            merged_df = merged_df[merged_df['Count_oracle'] != 0]

            merged_df['Status'] = np.where(merged_df['Count_oracle'].to_numpy() == merged_df['Count_postgres'].to_numpy(),'Pass','Fail')
            count_ora = merged_df['Count_oracle'].to_numpy()
            count_pg = merged_df['Count_postgres'].to_numpy()

            np.seterr(divide='ignore', invalid='ignore')
            merged_df['Difference (percentage)'] = np.where((count_ora != 0),np.round((count_ora - count_pg)/count_ora * 100, 2),0)

            if key in objects :
                key = "Summary"
                df_dropped = merged_df.dropna(axis=1, how='all')
                summary = pd.concat([summary, df_dropped], ignore_index=True)
                summary_df = self.status_control(summary, input_status)
                summary_dict[key] = summary_df

                description[key] = key
                content_index[key] = f"#{key}"
                content_section = {'Summary': content_index['Summary']}

            elif key not in objects:
                if key != "DIFF: Function":
                    key = key.replace("[", "").replace("]", "").replace("TEST", "").title()
                    data_df = self.status_control(merged_df, input_status)
                    data_dict[key] = data_df
                    description[key] = key
                    content_index[key] = f"#{key}"

        content_section.update(content_index)
        summary_df.rename(columns = {'Oracle_Table':'Object Type'}, inplace = True)
        self.summary_graph(summary_df)

        return summary_dict,data_dict,description,content_section,schema,difference

    def summary_graph(self,summary_df):
        bar_width = 0.35
        x = summary_df["Object Type"]
        y_positions = np.arange(len(x))

        height_oracle = summary_df['Count_oracle']
        height_oracle = pd.to_numeric(summary_df['Count_oracle'], errors='coerce').fillna(0).astype(int)
        height_postgres = summary_df['Count_postgres']
        height_postgres = pd.to_numeric(summary_df['Count_postgres'], errors='coerce').fillna(0).astype(int)
        plt.bar(y_positions - bar_width/2, height_oracle, bar_width, label='Oracle', color='skyblue', align='center')
        plt.bar(y_positions + bar_width/2, height_postgres, bar_width, label='PostgreSQL', color='lightgrey', align='center')

        for i, (h_oracle, h_postgres) in enumerate(zip(height_oracle, height_postgres)):
            plt.annotate(str(h_oracle), (y_positions[i] - bar_width/2, h_oracle), ha='center', va='bottom', color='black')
            plt.annotate(str(h_postgres), (y_positions[i] + bar_width/2, h_postgres), ha='center', va='bottom', color='black')

        plt.xticks(y_positions, x, rotation = 45)
        plt.ylabel('Count')
        plt.xlabel('Object Type')
        plt.title('Comparison of Object between Oracle and PostgreSQL')
        plt.legend(labels = ["Oracle","PostgreSQL"])
        plt.tight_layout()
        plt.gcf().set_size_inches(10, 6)
        output_file_name = fr"Ora2pgValidation_summary.png"
        out_dir_path = self.os_inst.dcg_ora_validation_report_path(self.project_name,output_file_name)
        plt.savefig(out_dir_path) 
        plt.close() 

    def render(self,template,schema,summary_dict, data_dict,description,content_section,difference):
        output_file_name = fr"Ora2pgValidation_{schema}.html"
        out_dir_path = self.os_inst.dcg_ora_validation_report_path(self.project_name,output_file_name)

        rendered_html = template.render(schema=schema,summary=summary_dict,results=data_dict, description=description,content_section=content_section,count=difference)
        
        with open(out_dir_path, "w") as html_file:
            html_file.write(rendered_html)
        print(f"Ora2pg validation report generated successfully - Ora2pgValidation_{schema}.html")

    # def csv_output(merged_df):
    #      merged_df.to_csv('ora2pg_count_validation.csv', index = False)

    def ora2pg_schema_validation(self,input_status):
        template = self.load_template() 
        summary_dict,data_dict,description,content_section,schema,difference = self.execution(input_status)
        self.render(template,schema,summary_dict,data_dict,description,content_section,difference)
        return True
    # csv_output(merged_df)



