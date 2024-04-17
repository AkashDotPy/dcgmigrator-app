import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from database_operation.oracle import OracleDatabaseManagement
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.logging_operation import HandleLogging

class CodeConversionPlanning:
    def __init__(self, project_name):
        self.project_name = project_name
        self.ora_inst = OracleDatabaseManagement(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def load_template(self):
        env = Environment(loader=FileSystemLoader('code_conversion_matrix'))
        template1 = env.get_template("template1.html")
        summary_template = env.get_template("summary.html")
        tableinfo_template = env.get_template("tableinfo.html")
        procedureinfo_template = env.get_template("procedureinfo.html")
        code_conversion_template = env.get_template("codeconversion.html")
        return template1, summary_template, tableinfo_template, procedureinfo_template, code_conversion_template

    def read_csv(self):
        return pd.read_csv(self.os_inst.os_join("code_conversion_matrix","code_conversion_planning.csv"))

    def connect_to_oracle(self):
        conn_oracle,ora_schema = self.ora_inst.schema_val_oraconn(self.project_name)
        return conn_oracle,ora_schema

    def pk(self,table_info):
        table_count = len(table_info)
        PK_count = table_info['pk'].value_counts()
        pk_cnt = PK_count.get("Y", 0)
        non_pk_count = table_info['pk'].value_counts()
        non_pk_cnt = non_pk_count.get("N", 0)
        return table_count, pk_cnt, non_pk_cnt

    def csv_execution(self,project_name,ora_schema, csv_data, template1, tableinfo_template,summary_template , conn_oracle, procedureinfo_template, code_conversion_template,args_weeks):
        schema = ora_schema.upper()
        results = {}
        descriptions = {}
        table_count = {}
        pk_cnt = {}
        non_pk_cnt = {}
        num_rows_total = 0 
        render_chart = False

        if args_weeks == None:
            #If no.of week is not specified it is set to 10 Week.
            num_weeks = "10"
        else:
            num_weeks = args_weeks 
        
        filtered_data = csv_data[csv_data["type"] != "summary"]
        file_names = filtered_data["outputname"].unique().tolist()
        unq = csv_data.type.unique()

        for unique_values in unq:
            results={}

            for index, row in csv_data[csv_data['type'] == unique_values].iterrows(): 
                outputname = row["outputname"]
                sql_query = row["sqlquery"]
                description = row["description"]
                plot = row["plot"]

                if unique_values == "summary":
                    replace_query = sql_query.replace('<<ORACLE_SCHEMA>>', schema.upper())
                    df_summary = pd.read_sql_query(replace_query, conn_oracle)
                    results[index] = df_summary
                    descriptions[index] = description

                    self.summary_line_plot(project_name,df_summary)
                    self.summary_donut_chart(project_name,df_summary)

                elif unique_values == "tableinfo":
                    if plot=="GRAPH":
                        replace_query = sql_query.replace('<<ORACLE_SCHEMA>>', schema.upper())
                        table_info = pd.read_sql_query(replace_query, conn_oracle)
                        table_count, pk_cnt, non_pk_cnt = self.pk(table_info)
                        results[index] = table_info
                        descriptions[index] = description
                        num_rows = table_info['num_rows_approx'].sum()
                        num_rows_total += num_rows
                        sum_lob = table_info["lobsize"].sum()
                        sum_nonlob = table_info["nonlobsize"].sum()
                        if sum_lob != 0 or sum_nonlob != 0:
                            render_chart = True
                            if render_chart:
                                self.create_pie_chart(project_name,table_info)

                        self.partition_pie_chart(project_name,table_info)
                        self.pk_pie_chart(project_name,table_info)

                    else:
                        table_info = pd.read_sql_query(sql_query, conn_oracle)
                        results[index] = table_info
                        descriptions[index] = description
                elif unique_values == "procedureinfo":
                    if plot=="GRAPH":
                        replace_query = sql_query.replace('<<ORACLE_SCHEMA>>', schema.upper())
                        procedure_info = pd.read_sql_query(replace_query, conn_oracle)
                        results[index] = procedure_info
                        descriptions[index] = description
                        self.referencecount_pie_chart(project_name,procedure_info)
                    if plot=="GRAPH_1":
                        replace_query = sql_query.replace('<<ORACLE_SCHEMA>>', schema.upper())
                        procedure_info_1 = pd.read_sql_query(replace_query, conn_oracle)
                        results[index] = procedure_info_1
                        descriptions[index] = description
                        self.referencecount_2_pie_chart(project_name,procedure_info_1)
                    else:
                        replace_query = sql_query.replace('<<ORACLE_SCHEMA>>', schema.upper())
                        procedure_info_2 = pd.read_sql_query(replace_query, conn_oracle)
                        results[index] = procedure_info_2
                        descriptions[index] = description

                elif unique_values == "codeconversionplanning":
                    if plot=="GRAPH":
                        replace_query = sql_query.replace('<<ORACLE_SCHEMA>>', schema.upper()).replace('<<NO_OF_WEEK>>', num_weeks)
                        code_conversion_plan = pd.read_sql_query(replace_query, conn_oracle)
                        results[index] = code_conversion_plan
                        descriptions[index] = description
                        self.generate_stacked_bar_chart(project_name,code_conversion_plan)
                        self.plot_count_of_object_types_over_weeks(project_name,code_conversion_plan)
                        self.plot_object_counts(project_name,code_conversion_plan)
                else:
                    replace_query = sql_query.replace('<<ORACLE_SCHEMA>>', schema.upper())
                    result = pd.read_sql_query(replace_query, conn_oracle)
                    results[index] = result
                    descriptions[index] = description


                if unique_values != "summary" and unique_values!="tableinfo" and unique_values!='procedureinfo' and unique_values !='codeconversionplanning':
                    rendered_html = template1.render(results=results, description=descriptions)
                    file_name = rf"{unique_values}.html"
                    html_directory = self.os_inst.code_conv_report_html_path(project_name,file_name)
                    with open(html_directory, "w") as html_file:
                        html_file.write(rendered_html)

                elif unique_values=="tableinfo":
                    rendered_html = tableinfo_template.render(render_chart=render_chart,schema=schema.lower(),table_count=table_count,pk_count=pk_cnt,non_pk=non_pk_cnt,results=results, description=descriptions,num_rows_total=num_rows_total)

                    file_name = rf"{unique_values}.html"
                    html_directory = self.os_inst.code_conv_report_html_path(project_name,file_name)
                    with open(html_directory, "w") as html_file:
                        html_file.write(rendered_html)

                elif unique_values=="procedureinfo":
                    rendered_html = procedureinfo_template.render(schema=schema.lower(),results=results, description=descriptions)
                    file_name = rf"{unique_values}.html"
                    html_directory = self.os_inst.code_conv_report_html_path(project_name,file_name)
                    with open(html_directory, "w") as html_file:
                        html_file.write(rendered_html)

                elif unique_values=="codeconversionplanning":
                    rendered_html = code_conversion_template.render(schema=schema.lower(),results=results, description=descriptions)
                    file_name = rf"{unique_values}.html"
                    html_directory = self.os_inst.code_conv_report_html_path(project_name,file_name)
                    with open(html_directory, "w") as html_file:
                        html_file.write(rendered_html)

                else:
                    rendered_html1 = summary_template.render(schema=schema.lower(),sheetname=file_names, results=results, description=descriptions)
                    file_name = rf"{unique_values}.html"
                    html_directory = self.os_inst.code_conv_report_html_path(project_name,file_name)
                    with open(html_directory, "w") as html_file:
                        html_file.write(rendered_html1)

        self.logger.info(f"Code Conversion matrix executed successfully\nReport: {html_directory}")

        return df_summary, table_info, procedure_info, procedure_info_1, code_conversion_plan

    def summary_line_plot(self,project_name,df_summary):

        if len(df_summary.index) != 0:
            object_types = df_summary["object_type"]
            cnt_objects = df_summary["cnt_obj"]

            for x, y in zip(object_types, cnt_objects):
                plt.text(x, y, f'{y}', ha='right', va='bottom')

            plt.plot(object_types, cnt_objects, marker='o', linestyle='-')
            plt.xlabel('Object Type')
            plt.ylabel('Count of Objects')
            plt.title('Count of Objects by Object Type')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            file_name = "summaryLinePlot.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory,format='png')
            plt.close()

    def summary_donut_chart(self,project_name,df_summary):\

        if len(df_summary.index) != 0:
            objecttype_colors = {
                'TABLE': '#80dfae',
	            'PARTITION': '#2db26d',
                'GRANT': '#134c2f',
                'TRIGGER': '#d2cd4d',
                'TYPE': '#b2ad2d',
                'VIEW': '#ecb3b3',
                'MATERIALIZED VIEW': '#d24d4d',
                'FUNCTION': '#80c2df',
                'PROCEDURE': '#2d89b2',
                'PACKAGE': '#315a82',
                'SEQUENCE_VALUES': '#a48ad5'
            }

            default_color = '#a4883b'
            object_types = df_summary["object_type"]
            locations = df_summary["loc"]

            explode = [0.05] * len(object_types)
            # colors = [objecttype_colors[obj_type] for obj_type in object_types]
            colors = [objecttype_colors.get(objtype, default_color) for objtype in object_types]
            plt.pie(locations, colors=colors,
                    autopct=lambda p: f'{int(p * sum(locations) / 100)}', pctdistance=0.85,
                    explode=explode)

            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            plt.legend(object_types, title="Object Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            plt.title('Object types and LOC')
            plt.tight_layout()
            file_name = r"summaryDonutChart.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory ,format='png')
            plt.close()

    def create_pie_chart(self,project_name,table_info):
        if len(table_info.index) != 0:
            object_types = df_summary["object_type"]
            cnt_objects = df_summary["cnt_obj"]

            for x, y in zip(object_types, cnt_objects):
                plt.text(x, y, f'{y}', ha='right', va='bottom')

            plt.plot(object_types, cnt_objects, marker='o', linestyle='-')
            plt.xlabel('Object Type')
            plt.ylabel('Count of Objects')
            plt.title('Count of Objects by Object Type')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            file_name = "summaryLinePlot.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory,format='png')
            plt.close()

    def summary_donut_chart(self,project_name,df_summary):
        if len(df_summary.index) != 0:
            objecttype_colors = {
                'TABLE': '#80dfae',
	            'PARTITION': '#2db26d',
                'GRANT': '#134c2f',
                'TRIGGER': '#d2cd4d',
                'TYPE': '#b2ad2d',
                'VIEW': '#ecb3b3',
                'MATERIALIZED VIEW': '#d24d4d',
                'FUNCTION': '#80c2df',
                'PROCEDURE': '#2d89b2',
                'PACKAGE': '#315a82',
                'SEQUENCE_VALUES': '#a48ad5'
            }

            default_color = '#a4883b'
            object_types = df_summary["object_type"]
            locations = df_summary["loc"]

            explode = [0.05] * len(object_types)
            # colors = [objecttype_colors[obj_type] for obj_type in object_types]
            colors = [objecttype_colors.get(objtype, default_color) for objtype in object_types]
            plt.pie(locations, colors=colors,
                    autopct=lambda p: f'{int(p * sum(locations) / 100)}', pctdistance=0.85,explode=explode)

            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            plt.legend(object_types, title="Object Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            plt.title('Object types and LOC')
            plt.tight_layout()
            file_name = r"summaryDonutChart.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory ,format='png')
            plt.close()

    def create_pie_chart(self,project_name,table_info):
        if len(table_info.index) != 0:
            LOB = table_info["lobsize"].sum()
            NONLOB = table_info["nonlobsize"].sum()

            labels = ['lobsize', 'nonlobsize']
            sizes = [LOB, NONLOB]
            colors = ['#4A90E2', '#B9C3F5']
            sum_values = sum(sizes)

            plt.pie(sizes, colors=colors, labels=labels, autopct=lambda p: f'{p * sum_values / 100}')

            plt.axis('equal')
            plt.legend(loc='upper right')
            plt.title('lobsize and nonlobsize')
            file_name = r"lob_cnt.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def pk_pie_chart(self,project_name,table_info):
        if len(table_info.index) != 0:
            pk_counts = table_info['pk'].value_counts()
            count_Y = pk_counts.get('Y', 0)
            count_N = pk_counts.get('N', 0)
            labels = ['Y', 'N']
            colors = ['#4A90E2', '#B9C3F5']
            counts = [count_Y, count_N]
            plt.pie(counts, colors=colors, labels=labels, startangle=90, autopct=lambda p: f'{int(p * sum(counts) / 100)}')
            plt.axis('equal')
            plt.legend(loc='upper right')
            plt.title('PRIMARYKEY AND NON-PRIMARYKEY')
            file_name = r"pk_count.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def partition_pie_chart(self,project_name,table_info):
        if len(table_info.index) != 0:
            partition_counts = table_info['PARTITION?'].value_counts()
            count_Yes = partition_counts.get('YES', 0)
            count_No = partition_counts.get('NO', 0)
            colors = ['#4A90E2', '#B9C3F5']
            plt.pie([count_Yes, count_No],  colors=colors,labels=['YES', 'NO'], autopct=lambda p: f'{int(p * sum([count_Yes,count_No]) / 100)}', startangle=90)
            plt.axis('equal')
            plt.legend(labels=['YES', 'NO'])  
            plt.title('PARTITION AND NON-PARTITION')
            file_name = r"partition_count.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def referencecount_pie_chart(self,project_name,procedure_info):
        if len(procedure_info.index) != 0:
            top_functions = procedure_info.head(5)
            function_names = top_functions['referenced_name'].tolist()
            counts = top_functions['COUNT(1)'].tolist()
            colors = ['#4A90E2', '#6FA1ED', '#94B2F8', '#B9C3F5', '#CED4F9', '#E3E9FD', '#F8FAFE']
            plt.figure(figsize=(8, 6)) 
            patches, _, _ = plt.pie(counts, colors=colors, labels=None, startangle=140, autopct='',labeldistance=0.7)
            for patch, label in zip(patches, counts):
                angle = patch.theta1 + (patch.theta2 - patch.theta1) / 2
                angle_rad = np.deg2rad(angle)
                radius = 0.7 * patch.r 
                x = radius * np.cos(angle_rad)
                y = radius * np.sin(angle_rad)
                plt.text(x, y, label, ha='center', va='center', color='black', fontsize=10)
            plt.legend(patches, function_names, loc='upper center', bbox_to_anchor=(1, 1))
            plt.axis('equal') 
            plt.title('Top 5 Function Names')
            file_name = r"reference_pie_chart.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def referencecount_2_pie_chart(self,project_name,procedure_info_1):
        if len(procedure_info_1.index) != 0:
            referenced_names = procedure_info_1['referenced_name'].tolist()
            counts = procedure_info_1['refer_count'].tolist()
            colors = ['#4A90E2', '#6FA1ED', '#94B2F8', '#B9C3F5', '#CED4F9', '#E3E9FD', '#F8FAFE']
            plt.figure(figsize=(8, 6)) 
            patches, _, _ = plt.pie(counts, colors=colors, labels=None, autopct='', startangle=140, labeldistance=0.7)
            for patch, count in zip(patches, counts):
                angle = (patch.theta2 - patch.theta1) / 2 + patch.theta1
                x = patch.r * 0.5 * np.cos(np.deg2rad(angle))
                y = patch.r * 0.5 * np.sin(np.deg2rad(angle))
                plt.text(x, y, str(count), ha='center', va='center', color='black')
            plt.legend(patches, referenced_names, loc='upper center',bbox_to_anchor=(1, 1))
            plt.axis('equal') 
            plt.title('Top 5 Referenced Names')
            file_name = r"referenced_name_pie_chart.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()
            pk_counts = table_info['pk'].value_counts()
            count_Y = pk_counts.get('Y', 0)
            count_N = pk_counts.get('N', 0)
            labels = ['Y', 'N']
            colors = ['#4A90E2', '#B9C3F5']
            counts = [count_Y, count_N]
            plt.pie(counts, colors=colors, labels=labels, startangle=90, autopct=lambda p: f'{int(p * sum(counts) / 100)}')
            plt.axis('equal')
            plt.legend(loc='upper right')
            plt.title('PRIMARYKEY AND NON-PRIMARYKEY')
            file_name = r"pk_count.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def partition_pie_chart(self,project_name,table_info):
        if len(table_info.index) != 0:
            partition_counts = table_info['PARTITION?'].value_counts()
            count_Yes = partition_counts.get('YES', 0)
            count_No = partition_counts.get('NO', 0)
            colors = ['#4A90E2', '#B9C3F5']
            plt.pie([count_Yes, count_No],  colors=colors,labels=['YES', 'NO'], autopct=lambda p: f'{int(p * sum([count_Yes,count_No]) / 100)}', startangle=90)
            plt.axis('equal')
            plt.legend(labels=['YES', 'NO'])  
            plt.title('PARTITION AND NON-PARTITION')
            file_name = r"partition_count.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def referencecount_pie_chart(self,project_name,procedure_info):
        if len(procedure_info.index) != 0:
            top_functions = procedure_info.head(5)
            function_names = top_functions['referenced_name'].tolist()
            counts = top_functions['COUNT(1)'].tolist()
            colors = ['#4A90E2', '#6FA1ED', '#94B2F8', '#B9C3F5', '#CED4F9', '#E3E9FD', '#F8FAFE']
            plt.figure(figsize=(8, 6)) 
            patches, _, _ = plt.pie(counts, colors=colors, labels=None, startangle=140, autopct='',labeldistance=0.7)
            for patch, label in zip(patches, counts):
                angle = patch.theta1 + (patch.theta2 - patch.theta1) / 2
                angle_rad = np.deg2rad(angle)
                radius = 0.7 * patch.r 
                x = radius * np.cos(angle_rad)
                y = radius * np.sin(angle_rad)
                plt.text(x, y, label, ha='center', va='center', color='black', fontsize=10)
            plt.legend(patches, function_names, loc='upper center', bbox_to_anchor=(1, 1))
            plt.axis('equal') 
            plt.title('Top 5 Function Names')
            file_name = r"reference_pie_chart.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def referencecount_2_pie_chart(self,project_name,procedure_info_1):
        if len(procedure_info_1.index) != 0:
            referenced_names = procedure_info_1['referenced_name'].tolist()
            counts = procedure_info_1['refer_count'].tolist()
            colors = ['#4A90E2', '#6FA1ED', '#94B2F8', '#B9C3F5', '#CED4F9', '#E3E9FD', '#F8FAFE']
            plt.figure(figsize=(8, 6)) 
            patches, _, _ = plt.pie(counts, colors=colors, labels=None, autopct='', startangle=140, labeldistance=0.7)
            for patch, count in zip(patches, counts):
                angle = (patch.theta2 - patch.theta1) / 2 + patch.theta1
                x = patch.r * 0.5 * np.cos(np.deg2rad(angle))
                y = patch.r * 0.5 * np.sin(np.deg2rad(angle))
                plt.text(x, y, str(count), ha='center', va='center', color='black')
            plt.legend(patches, referenced_names, loc='upper center',bbox_to_anchor=(1, 1))
            plt.axis('equal') 
            plt.title('Top 5 Referenced Names')
            file_name = r"referenced_name_pie_chart.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def generate_stacked_bar_chart(self,project_name,code_conversion_plan):
        if len(code_conversion_plan.index) != 0:
            filtered_data = code_conversion_plan[['week', 'objecttype', 'loc']]
            pivot_df = filtered_data.groupby(['week', 'objecttype'])['loc'].sum().unstack(fill_value=0)
            num_weeks = len(pivot_df.index)
            figsize_width = max(12, num_weeks * 0.5)    
            objecttype_colors = {
                'TABLE': '#80dfae',
	            'PARTITION': '#2db26d',
                'GRANT': '#134c2f',
                'TRIGGER': '#d2cd4d',
                'TYPE': '#b2ad2d',
                'VIEW': '#ecb3b3',
                'MATERIALIZED VIEW': '#d24d4d',
                'FUNCTION': '#80c2df',
                'PROCEDURE': '#2d89b2',
                'PACKAGE': '#315a82',
                'SEQUENCE_VALUES': '#a48ad5'
            }

            default_color = '#a4883b'
            colors = [objecttype_colors.get(objtype, default_color) for objtype in pivot_df.columns]

            ax = pivot_df.plot(kind='bar', stacked=True, figsize=(figsize_width, 6), color = colors)
            plt.xlabel('Week')
            plt.ylabel('LOC')
            plt.title('LOC by Object Type for All Weeks')
            plt.xticks(rotation=45)
            plt.legend(title='Object Type')
            for i, week in enumerate(pivot_df.index):
                y_offset = 0
                for objtype in pivot_df.columns:
                    loc_value = pivot_df.loc[week, objtype]
                    if loc_value != 0:
                        ax.text(i, y_offset + loc_value / 2, str(loc_value), color='black', ha='center')
                    y_offset += loc_value
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.2)  
            file_name = r"loc_by_object_type.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def plot_count_of_object_types_over_weeks(self, project_name, code_conversion_plan):
        if len(code_conversion_plan.index) != 0:
            count_data = code_conversion_plan.groupby(['week_no', 'objecttype']).size().reset_index(name='count')
            objtype_counts = code_conversion_plan['objecttype'].value_counts()

            objecttype_colors = {
                'TABLE': '#80dfae',
	            'PARTITION': '#2db26d',
                'GRANT': '#134c2f',
                'TRIGGER': '#d2cd4d',
                'TYPE': '#b2ad2d',
                'VIEW': '#ecb3b3',
                'MATERIALIZED VIEW': '#d24d4d',
                'FUNCTION': '#80c2df',
                'PROCEDURE': '#2d89b2',
                'PACKAGE': '#315a82',
                'SEQUENCE_VALUES': '#a48ad5'
            }

            default_color = '#a4883b'

            fig, gnt = plt.subplots(figsize=(11, 6))
            unique_weeks = sorted(set(count_data['week_no']), key=lambda x: count_data['week_no'].tolist().index(x))
            x_tick_labels = unique_weeks
            x_pos = np.arange(len(x_tick_labels))
            gnt.set_xticks(x_pos)
            gnt.set_xticklabels(x_tick_labels, rotation=45, ha='right')
            y_pos = np.arange(len(objtype_counts)) * 10  
            y_tick_labels = [f'{objtype} ({count})' for objtype, count in objtype_counts.items()]
            gnt.set_yticks(y_pos)
            gnt.set_yticklabels(y_tick_labels)
            objtype_pos = {objtype: pos for pos, objtype in zip(y_pos, objtype_counts.index)}

            for _, row in count_data.iterrows():
                week_index = unique_weeks.index(row['week_no'])
                bar_position = (objtype_pos[row['objecttype']], 5)
                color = objecttype_colors.get(row['objecttype'], default_color)
                gnt.broken_barh([(week_index - 0.4, 0.8)], bar_position, facecolors=color)
                gnt.text(week_index, objtype_pos[row['objecttype']] + 2.5, row['count'], ha='center', va='center', color='black')

            plt.xlabel('WEEK_NO')
            plt.ylabel('Object Type (Count)')
            plt.title('Plot of Count of Object Types over Weeks')
            file_name = r"week_by_object_type.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name, file_name)
            plt.savefig(img_directory, format='png')
            plt.grid(True)
            plt.close()


    def plot_object_counts(self,project_name,code_conversion_plan):
        if len(code_conversion_plan.index) != 0:
            count_data = code_conversion_plan.groupby(['week', 'objecttype']).size().reset_index(name='count')
            count_data['week_no'] = count_data['week'].astype(str).str.extract('(\d+)').astype(int) 
            objtype_counts = code_conversion_plan['objecttype'].value_counts()
            objecttype_colors = {
                'TABLE': '#80dfae',
	            'PARTITION': '#2db26d',
                'GRANT': '#134c2f',
                'TRIGGER': '#d2cd4d',
                'TYPE': '#b2ad2d',
                'VIEW': '#ecb3b3',
                'MATERIALIZED VIEW': '#d24d4d',
                'FUNCTION': '#80c2df',
                'PROCEDURE': '#2d89b2',
                'PACKAGE': '#315a82',
                'SEQUENCE_VALUES': '#a48ad5'
            }

            default_color = '#a4883b'
            fig, ax = plt.subplots(figsize=(10, 6))
            for objtype in objtype_counts.index:
                objtype_data = count_data[count_data['objecttype'] == objtype]
                objtype_weeks = objtype_data['week_no']
                counts = objtype_data['count']
                color = objecttype_colors.get(objtype, default_color)
                ax.plot(objtype_weeks, counts, marker='o', label=objtype, color=color)
                for i, txt in enumerate(counts):
                    ax.annotate(txt, (objtype_weeks.iloc[i], counts.iloc[i]))
            ax.set_xlabel('Week')
            ax.set_ylabel('Count')
            ax.set_title('Count of Object Types over Weeks')
            ax.legend()
            ax.grid(True)
            plt.xticks(range(min(count_data['week_no']), max(count_data['week_no']) + 1)) 
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            file_name = r"week_by_object_type_line.png"
            img_directory = self.os_inst.code_conv_report_img_path(project_name,file_name)
            plt.savefig(img_directory, format='png')
            plt.close()

    def code_conv_planning(self,project_name,args_weeks):
        template1, summary_template, tableinfo_template, procedureinfo_template, code_conversion_template = self.load_template()
        csv_data = self.read_csv()
        conn_oracle,ora_schema = self.connect_to_oracle()
        self.csv_execution(project_name,ora_schema, csv_data, template1, tableinfo_template,summary_template , conn_oracle, procedureinfo_template, code_conversion_template,args_weeks) 
   
