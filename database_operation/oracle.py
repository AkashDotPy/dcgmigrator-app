import cx_Oracle
from sqlalchemy import create_engine,text 
from database_operation.sqlite import SqliteDatabaseManagement
from os_operation.os_handling import DirectoryPath
from dcgmigrator_core.logging_operation import HandleLogging
import re

# sqlite = SqliteDatabaseManagement()
# self.os_inst = DirectoryPath()
# log_inst = HandleLogging()
# self.logger = log_inst.handle_log()

class OracleDatabaseManagement:
    def __init__(self, project_name):
        self.project_name = project_name
        self.sqlite = SqliteDatabaseManagement(self.project_name)
        self.os_inst = DirectoryPath(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()
    
    def fetch_cred(self,project_name):
        # fetch oracle connection credentials from ora_config_details table
        result = self.sqlite.fetch_oracle_connection(project_name)
        for row in result:
            (key, value) = row

            if "oracle_user".casefold() in key.casefold():
                username = value

            if "oracle_pwd".casefold() in key.casefold():
                paswword = value

            if "oracle_dsn".casefold() in key.casefold() and "host=" in value:
                pattern = re.search(r"host=(.*?);service_name=(.*?);port=(.+)", value)
                host = pattern.group(1)
                service_name = pattern.group(2)
                port = pattern.group(3)

            if "ora_schema".casefold() in key.casefold():
                ora_schema = value

        return username,paswword,host,port,service_name,ora_schema
    
    def database_connection(self,username,paswword,host,port,service_name):
        db_url = f"oracle://{username}:{paswword}@{host}:{port}/?service_name={service_name}"
        engine = create_engine(db_url)
        connection = engine.raw_connection()
        cursor = connection.cursor()
        return cursor,connection,db_url
    
    def _fetch_modify_type(self,cursor,project_name,ora_schema):
        self.logger.info(f"\n Started running data type mapping on Column for oracle schema - {ora_schema.upper()}")
        output_lines = []
        modify_type_value = []
        modify_type_csv = []
        dir_path = r"databasescript"
        input_file_name = r"number_dt.sql"
        output_file_name = fr"{project_name}_number_recommendation.csv"
        # fetch query output from (number_dt.sql) PLSQL script 
        cursor.callproc("dbms_output.enable")
        file_path = self.os_inst.os_join(dir_path,input_file_name)
        with open(file_path, 'r') as file:
            query = file.read()
            replaced_query = query.replace("<<ORACLE_SCHEMA_NAME>>", ora_schema.upper())

        cursor.execute(replaced_query)

        statusVar = cursor.var(cx_Oracle.NUMBER)
        lineVar = cursor.var(cx_Oracle.STRING)

        while True:
            cursor.callproc("dbms_output.get_line", (lineVar, statusVar))
            if statusVar.getvalue() != 0:
              break
            output_lines.append(lineVar.getvalue())

        # filter modify_type key from PLSQL script  
        for line in output_lines:
            if "ORA2PG_MODIFY_TYPE" in line:
                match = re.search(r"MODIFY_TYPE(.+)", line)
                modify_type_value.append(match.group(0).split("*"))
            else:
                modify_type_csv.append(line.split("*"))

        try:
            # self.os_inst.report_path()
            file_path = self.os_inst.dcg_report_path(project_name,output_file_name,"NumberRecomm")
            with open(file_path, "w") as csv_file:
                for row in modify_type_csv:
                    csv_file.write(",".join(row) + "\n")
               
        except Exception as e:
            self.logger.error(f"Error : {e} \n Unable to create number data modify type report csv file")
            return;  
        
        self.logger.info(f"\n Completed Number data type mapping for oracle schema - {ora_schema.upper()}")
        self.logger.info(f"oracle schema - {ora_schema.upper()} - Modify number type - \n {modify_type_value}")

        return modify_type_value
    
    def insert_modify_type_config(self,project_name,modify_type_value):
        for key, value in modify_type_value:
            if key.casefold() in "ORA2PG_MODIFY_TYPE".casefold():
                key="MODIFY_TYPE"
            return self.sqlite.insert_ora2pgconfig(project_name, key, value)
            
    
    def number_modify_type(self, project_name):
        username,password,host,port,service_name,ora_schema= self.fetch_cred(project_name)
        cursor,connection,db_url = self.database_connection(username,password,host,port,service_name)
        modify_type_value = self._fetch_modify_type(cursor,project_name,ora_schema)
        if self.insert_modify_type_config(project_name,modify_type_value):
            self.sqlite.refresh_ora2pgconfig(project_name)
            cursor.close()
            connection.close()
            return True
        else:
            return False
    
    def schema_val_oraconn(self,project_name):
        username,password,host,port,service_name,ora_schema = self.fetch_cred(project_name)
        try:
            db_url = f"oracle://{username}:{password}@{host}:{port}/?service_name={service_name}"
            engine = create_engine(db_url)
            conn_oracle = engine.connect()
            if conn_oracle:
                return conn_oracle, ora_schema
            
        except Exception as e:
            raise e

    def view_count(self,project_name):
        conn_oracle, ora_schema = self.schema_val_oraconn(project_name)
        result = conn_oracle.execute(text(f"SELECT CASE WHEN COUNT(1) > 500 THEN 'Y' ELSE 'N' END AS VIEW_CNT FROM ALL_VIEWS WHERE OWNER = '{ora_schema.upper()}'"))
        return result.fetchone()[0]

    def oracle_package_exists(self,project_name, packagename):
        conn_oracle, ora_schema = self.schema_val_oraconn(project_name)
        result = conn_oracle.execute(text(f"SELECT 1 FROM DBA_OBJECTS WHERE OBJECT_TYPE='PACKAGE' AND STATUS ='VALID' AND OBJECT_NAME='{packagename.upper()}'"))
        if result.fetchone() is not None:
            return True
        else:
            return False
    
    def validate_oracle(self,project_name):
        try:
            conn_oracle, ora_schema = self.schema_val_oraconn(project_name)
            if conn_oracle.execute(text("SELECT * from v$version")).fetchone()[0] is not None:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"{e}")
            return False

    def validate_oracle_schema(self,project_name, ora_schema_input=None):
        try:
            conn_oracle, ora_schema = self.schema_val_oraconn(project_name)
            if ora_schema_input is None:
                if conn_oracle.execute(text(f"select 1 from dba_users where username = upper('{ora_schema}')")).fetchone() is not None:
                    return True
                else:
                    return False
            else:
                if conn_oracle.execute(text(f"select 1 from dba_users where username = upper('{ora_schema_input}')")).fetchone() is not None:
                    return True
                else:
                    return False
        except Exception as e:
            self.logger.error(f"{e}")
            return False

    def oracle_objects(self,project_name):
        try:
            conn_oracle, ora_schema = self.schema_val_oraconn(project_name)
            query = """SELECT 'GRANT' AS OBJECT_TYPE, 2 AS SEQ_ORDER FROM DUAL WHERE EXISTS
                        (SELECT 1 FROM all_objects
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>'))
                        UNION ALL
                        SELECT CASE  OBJECT_TYPE WHEN 'TABLE PARTITION' THEN 'PARTITION'
                        WHEN 'MATERIALIZED VIEW' THEN 'MVIEW' ELSE OBJECT_TYPE END,
                        CASE OBJECT_TYPE
                        WHEN 'GRANT' THEN 2
                        WHEN 'VIEW' THEN 3
                        WHEN 'TRIGGER' THEN 4
                        WHEN 'TYPE' THEN 5
                        WHEN 'FUNCTION' THEN 6
                        WHEN 'PROCEDURE' THEN 7
                        WHEN 'PACKAGE' THEN 8
                        WHEN 'MATERIALIZED VIEW' THEN 9
                        WHEN 'SEQUENCE' THEN 10
                        WHEN 'TABLE PARTITION' THEN 11
                        WHEN 'TABLE' THEN 1
                        END AS SEQORDER
                        FROM all_objects
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>')
                        and object_type in
                        (
                        'VIEW',
                        'TRIGGER',
                        'TYPE',
                        'FUNCTION',
                        'PROCEDURE',
                        'PACKAGE',
                        'SEQUENCE',
                        'TABLE',
                        'TABLE PARTITION'
                        )
                        GROUP BY OBJECT_TYPE
                        order by 2"""
            
            replace_value = query.replace("<<ORACLE_SCHEMA>>",ora_schema)
            result = conn_oracle.execute(text(replace_value))
            return result.fetchall()
            
        except Exception as e:
            self.logger.error(f"{e.__cause__}")

    def pre_data_obj(self,project_name):
        try:
            conn_oracle, ora_schema = self.schema_val_oraconn(project_name)

            query = r"""SELECT 'CONSTRAINTS' AS OBJECT_TYPE, 3 AS SEQ_ORDER FROM DUAL WHERE EXISTS
                        (SELECT 1 FROM all_CONSTRAINTS
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>') and CONSTRAINT_TYPE not in ('P','R'))
                        UNION ALL
                        SELECT 'EXTENSION' AS OBJECT_TYPE , 6  AS SEQ_ORDER FROM DUAL WHERE EXISTS
                        (SELECT 1 FROM all_objects
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>'))
                        UNION ALL
                        SELECT CASE  OBJECT_TYPE WHEN 'TABLE PARTITION' THEN 'PARTITION'
                        WHEN 'MATERIALIZED VIEW' THEN 'MVIEW' ELSE OBJECT_TYPE END,
                        CASE OBJECT_TYPE
                        WHEN 'SEQUENCE' THEN 5
                        WHEN 'TABLE PARTITION' THEN 4
                        WHEN 'TABLE' THEN 2
                        WHEN 'TYPE' THEN 1
                        END AS SEQORDER
                        FROM all_objects
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>')
                        and object_type in
                        (
                        'SEQUENCE',
                        'TABLE',
                        'TABLE PARTITION',
                        'TYPE'
                        )
                        GROUP BY OBJECT_TYPE
                        ORDER BY SEQ_ORDER"""
            replace_value = query.replace("<<ORACLE_SCHEMA>>",ora_schema)
            result = conn_oracle.execute(text(replace_value))
            return result.fetchall()
        
        except Exception as e:
            self.logger.error(f"{e.__cause__}")

    def post_data_obj(self,project_name):
        try:
            conn_oracle, ora_schema = self.schema_val_oraconn(project_name)

            query = r"""SELECT 'GRANT' AS OBJECT_TYPE, 1 AS SEQ_ORDER FROM DUAL WHERE EXISTS
                        (SELECT 1 FROM all_objects
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>'))
                        UNION ALL
                        SELECT 'FKEYS' AS OBJECT_TYPE, 11 AS SEQ_ORDER FROM DUAL WHERE EXISTS
                        (SELECT 1 FROM all_CONSTRAINTS
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>') and CONSTRAINT_TYPE  in ('R'))
                        UNION ALL
                        SELECT 'INDEXES' AS OBJECT_TYPE, 2 AS SEQ_ORDER FROM DUAL WHERE EXISTS
                        (SELECT 1 FROM all_indexes
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>'))
                          UNION ALL
                        SELECT 'TRIGGER_SANITY' AS OBJECT_TYPE , 10 AS  SEQ_ORDER FROM DUAL WHERE EXISTS
                        (SELECT 1 FROM ALL_TRIGGERS WHERE OWNER =UPPER('<<ORACLE_SCHEMA>>'))
                        UNION ALL
                        SELECT CASE  OBJECT_TYPE WHEN 'TABLE PARTITION' THEN 'PARTITION'
                        WHEN 'MATERIALIZED VIEW' THEN 'MVIEW'
                        WHEN 'SEQUENCE' THEN 'SEQUENCE_VALUES'
                        ELSE OBJECT_TYPE END,
                        CASE OBJECT_TYPE
                        WHEN 'VIEW' THEN 4
                        WHEN 'TRIGGER' THEN 3
                        WHEN 'FUNCTION' THEN 5
                        WHEN 'PROCEDURE' THEN 6
                        WHEN 'PACKAGE' THEN 7
                        WHEN 'MATERIALIZED VIEW' THEN 8
                        WHEN 'SEQUENCE' THEN 9
                        END AS SEQORDER
                        FROM all_objects
                        WHERE  OWNER = UPPER('<<ORACLE_SCHEMA>>')
                        and object_type in
                        (
                        'VIEW',
                        'TRIGGER',
                        'FUNCTION',
                        'PROCEDURE',
                        'PACKAGE',
                        'SEQUENCE'
                        )
                        GROUP BY OBJECT_TYPE
                        ORDER BY SEQ_ORDER"""
            replace_value = query.replace("<<ORACLE_SCHEMA>>",ora_schema)
            result = conn_oracle.execute(text(replace_value))
            return result.fetchall()
        
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False



        

            
        
        
                

   





