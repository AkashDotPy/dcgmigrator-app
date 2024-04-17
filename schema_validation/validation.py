from database_operation.oracle import OracleDatabaseManagement
from database_operation.postgres import PostgresDatabase
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.logging_operation import HandleLogging
import pandas as pd
from sqlalchemy import create_engine
from jinja2 import Environment, FileSystemLoader
import os
from matplotlib import pyplot as plt
import numpy as np

# csv_path = r"schema_validation\schemacomparesql.csv"
merged_summary = pd.DataFrame()

class Validation:
    def __init__(self,project_name):
        self.project_name = project_name
        self.ora_inst = OracleDatabaseManagement(self.project_name)
        self.pg_inst = PostgresDatabase(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def load_environment(self): 
        env = Environment(loader=FileSystemLoader('schema_validation'))
        template = env.get_template(r"sample_validation_template.html")
        return template

    def connection(self,project_name):
        conn_oracle,ora_schema = self.ora_inst.schema_val_oraconn(project_name)
        if self.pg_inst.schema_val_pgconn(project_name):
            conn_postgres,pg_schema = self.pg_inst.schema_val_pgconn(project_name)
            return conn_oracle, conn_postgres, ora_schema, pg_schema
        else:
            return None

    def read_csv (self,conn_oracle, conn_postgres, ora_schema, pg_schema,project_name):
        dir_path = r"schema_validation"
        file_name = r"schemacomparesql.csv"
        file_path = self.os_inst.os_join(dir_path,file_name)
        data = pd.read_csv(file_path)
        desired_join = "outer"
        valid_joins = ["right", "left", "outer", "inner"]
        if desired_join not in valid_joins:
            print("Invalid input. Applying default outer join")
            desired_join = "outer"    

        missing_rows = {}
        section_titles =  {}
        descriptions = {}
        missing_rows_index = 1

        for index,row in data.iterrows():
            oracle_query = row["oracle_sql"]
            postgres_query = row["postgresql_sql"]
            ref_col = list(row['refcol'].split(","))
            desired_missing_data = row['dbtovalidate']  
            section_title = row["module"]
            description = row["description"]

            replaced_value1 = oracle_query.replace("<<ORACLE_SCHEMA_NAME>>", ora_schema.upper())
            replaced_value2 = postgres_query.replace("<<POSTGRES_SCHEMA_NAME>>", pg_schema.lower())

            ora_name = ora_schema
            df1 = pd.read_sql_query(replaced_value1, conn_oracle )
            df2 = pd.read_sql_query(replaced_value2, conn_postgres)
            
            merged_df = df1.merge(df2, on=ref_col, sort=True, how=desired_join, indicator="ind", suffixes=('_oracle', '_postgres'))
            for f in merged_df.columns:
                if merged_df[f].dtype == "object":
                    merged_df[f] = merged_df[f].fillna("")

            if desired_missing_data == "postgres":
                missing_rows[missing_rows_index] = merged_df[merged_df['ind'] == "left_only"].loc[:, ~merged_df.columns.isin(["ind"]) & ~merged_df.columns.str.endswith('_postgres')]
                section_titles[missing_rows_index] = section_title
                descriptions[missing_rows_index] = description
                missing_rows_index=missing_rows_index+1
            elif desired_missing_data == "oracle":
                missing_rows[missing_rows_index] = merged_df[merged_df['ind'] == "right_only"].loc[:, ~merged_df.columns.isin(["ind"]) & ~merged_df.columns.str.endswith('_oracle')]
                section_titles[missing_rows_index] = section_title
                descriptions[missing_rows_index] = description
                missing_rows_index=missing_rows_index+1
            elif desired_missing_data == "both":
                missing_rows[missing_rows_index] = merged_df[merged_df['ind'] == "both"].loc[:, merged_df.columns != "ind"]
                section_titles[missing_rows_index] = section_title
                descriptions[missing_rows_index] = description
                missing_rows_index=missing_rows_index+1
            elif desired_missing_data == "summary":
                missing_rows[missing_rows_index] = merged_df[merged_df['ind'] == "both"].loc[:, merged_df.columns.str.startswith(("oracle","postgres"))].drop_duplicates()
                section_titles[missing_rows_index] = section_title
                descriptions[missing_rows_index] = description
                missing_rows_index=missing_rows_index+1
            else:
                merged_summary = merged_df.loc[:, merged_df.columns != "ind"].fillna(0)
                section_titles[0] = section_title
                descriptions[0] = description
                missing_rows[0] = merged_summary 

                self.generate_summary_chart(merged_summary,ora_name,project_name)
                
        return index, df1, df2, ref_col, desired_missing_data,desired_join,missing_rows, merged_summary, section_titles,descriptions,ora_name,project_name

    def generate_summary_chart(self,merged_summary,ora_name,project_name):
        bar_width = 0.35
        x = merged_summary["object_type"]
        y_positions = np.arange(len(x))

        height_oracle = merged_summary['cnt_oracle']
        height_oracle = pd.to_numeric(merged_summary['cnt_oracle'], errors='coerce').fillna(0).astype(int)
        height_postgres = merged_summary['cnt_postgres']
        height_postgres = pd.to_numeric(merged_summary['cnt_postgres'], errors='coerce').fillna(0).astype(int)

        plt.bar(y_positions - bar_width/2, height_oracle, bar_width, label='Oracle', color='lightgrey', align='center')
        plt.bar(y_positions + bar_width/2, height_postgres, bar_width, label='PostgreSQL', color='skyblue', align='center')

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
        file_name = f"schemareport.png"
        file_path = self.os_inst.schema_Validation_report_path(project_name,file_name,ora_name)
        plt.savefig(file_path) 
        plt.close()   

    def generate_html(self,missing_rows,template,section_titles,descriptions,ora_name,project_name):
        # print(ora_name)
        rendered_html = template.render(missing_rows=missing_rows,section_titles=section_titles,descriptions=descriptions,ora_name=ora_name)

        file_name = f"oracle_pg_validation_{ora_name}.html"
        file_path = self.os_inst.schema_Validation_report_path(project_name,file_name,ora_name)

        with open(file_path, "w") as html_file:
            html_file.write(rendered_html)

        self.logger.info(f"Schema validation report for {ora_name} is generated \n{file_path}")
        

    def test_schema(self,project_name):
        if self.connection(project_name):
            conn_oracle, conn_postgres, ora_schema, pg_schema = self.connection(project_name)
            index, df1, df2, ref_col, desired_missing_data,desired_join,missing_rows, merged_summary,section_titles,descriptions,ora_name,project_name = self.read_csv (conn_oracle, conn_postgres, ora_schema, pg_schema,project_name)
            template = self.load_environment()
            self.generate_html(missing_rows,template,section_titles,descriptions,ora_name,project_name)
            self.read_csv (conn_oracle, conn_postgres, ora_schema, pg_schema,project_name)
            conn_oracle.close()
            conn_postgres.close()


    











