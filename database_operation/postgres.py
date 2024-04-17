from sqlalchemy import create_engine, text
from database_operation.sqlite import SqliteDatabaseManagement
from os_operation.os_handling import DirectoryPath
import re
from dcgmigrator_core.logging_operation import HandleLogging

class PostgresDatabase:
    username = None
    password = None
    dbname = None
    host = None
    port = None
    pg_schema = None


    def __init__(self, project_name):
        self.project_name = project_name
        self.os_inst = DirectoryPath(self.project_name)
        self.sqlite = SqliteDatabaseManagement(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()
        # username,password,host,port,dbname,pg_schema = self.fetch_pg_cred(project_name)
    
    def connect_to_postgres(self,username,password,host,port,dbname,pg_schema):
        try:
            alchemy_pattern = fr"postgresql://{username}:{password}@{host}:{port}/{dbname}"
            engine = create_engine(alchemy_pattern)
            conn = engine.connect()
            return conn,engine
        except Exception as e:
            raise e

    def fetch_pg_cred_deploy(self,project_name):
        if self.sqlite.validate_target_connection(self.project_name):
            result = self.sqlite.fetch_postgres_connection(project_name)

            for row in result:
                (key, value) = row

                if "pg_user".casefold() in key.casefold():
                    username = value

                if "pg_pwd".casefold() in key.casefold():
                    password = value

                if "pg_dsn".casefold() in key.casefold() :
                    pattern = re.search(r"dbname=(.*?);host=(.*?);port=(.+)", value)
                    dbname = pattern.group(1)
                    host = pattern.group(2)
                    port = pattern.group(3)

                if "pg_schema".casefold() in key.casefold():
                    pg_schema = value

            # print(username,password,host,port,dbname,pg_schema)
            return username,password,host,port,dbname,pg_schema
        else:
            self.logger.error("Target database details missing in config\nPlease use upsert/create-target command.")
            return None

    def fetch_pg_cred(self,project_name):
        if self.sqlite.validate_target_connection(self.project_name):
            result = self.sqlite.fetch_postgres_connection(project_name)

            for row in result:
                (key, value) = row

                if "pg_user".casefold() in key.casefold():
                    global username 
                    username = value

                if "pg_pwd".casefold() in key.casefold():
                    global password
                    password = value

                if "pg_dsn".casefold() in key.casefold() :
                    pattern = re.search(r"dbname=(.*?);host=(.*?);port=(.+)", value)
                    global dbname 
                    dbname = pattern.group(1)
                    global host
                    host = pattern.group(2)
                    global port
                    port = pattern.group(3)

                if "pg_schema".casefold() in key.casefold():
                    global pg_schema
                    pg_schema = value
            # print(username,password,host,port,dbname,pg_schema)
            # return username,password,host,port,dbname,pg_schema
            return True
        else:
            self.logger.error("Target database details missing in config\nPlease use upsert/create-target command.")
            return None

    def schema_val_pgconn(self,project_name):
        if self.fetch_pg_cred(project_name):
            # username,password,host,port,dbname,pg_schema = self.fetch_pg_cred(project_name)
            db_url = fr"postgresql://{username}:{password}@{host}:{port}/{dbname}"
            engine = create_engine(db_url)
            conn_postgres = engine.connect()        
            return conn_postgres,pg_schema
        else:
            None
    
    def execution_conn(self,project_name):
        if self.fetch_pg_cred(project_name):
            conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
            return engine,conn,pg_schema
        else:
            None
    
    # def dep_execution_conn(self,project_name,sql_file):
    #     username,password,host,port,dbname,pg_schema = self.fetch_pg_cred(project_name)
    #     conn,engine = self.connect_to_postgres(username,password,host,port,dbname)
    #     try:
    #         conn.execute(text(sql_file))
    #         conn.commit()
    #     except Exception as excep:
    #         self.logger.error(f"{excep} \n Issue occured in DB Deployment)")
    #         return False
    #     finally:
    #         conn.close()
    #     return True
    
    def orafce(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    conn.execute(text("select true from pg_available_extensions where name ilike 'orafce'")).fetchone()
                    return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False

    def export_gtt(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    conn.execute(text("select true from pg_available_extensions where name ilike 'pgtt'")).fetchone()
                    return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False
    
    def dblink_conn(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    conn.execute(text("select true from pg_available_extensions where name ilike 'dblink' or name ilike 'pg_background'")).fetchone()
                    return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False

    def postgres_schema_check(self,project_name,schemaname):
        # username,password,host,port,dbname,pg_schema = self.fetch_pg_cred(project_name)
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    conn.execute(text(f"SELECT 1 exists FROM pg_catalog.pg_namespace n WHERE n.nspname ilike '{schemaname}'")).fetchone()
                    return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False

    def postgres_drop_schema(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    conn.execute(text(f"drop schema if exists {pg_schema} cascade"))
                    return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False


    def autonomous_transaction(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    if conn.execute(text("select true from pg_available_extensions where name ilike 'dblink'")).fetchone():
                        return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False

    def autonomous_transaction_pg_background(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    conn.execute(text("select true from pg_available_extensions where name ilike 'pg_background'")).fetchone()
                    return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False
        
    def oracle_fdw(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    if conn.execute(text(f"select true where exists (select 1 from pg_available_extensions where name ilike 'oracle_fdw')  and exists (select 1 from pg_catalog.pg_foreign_server s  JOIN pg_catalog.pg_foreign_data_wrapper f ON f.oid=s.srvfdw  where  s.srvname ~ '^(orcl)$') and exists (select 1 FROM pg_catalog.pg_namespace n WHERE n.nspname ~ '^(ora2pg_fdw_import)$')  and (select count(1) FROM pg_catalog.pg_foreign_table ft INNER JOIN pg_catalog.pg_class c ON c.oid = ft.ftrelid INNER JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace INNER JOIN pg_catalog.pg_foreign_server s ON s.oid = ft.ftserver WHERE n.nspname ~ '^(ora2pg_fdw_import)$' AND pg_catalog.pg_table_is_visible(c.oid)) > 0 ")).fetchone():
                        conn.execute = (text(f"CREATE FOREIGN TABLE ora2pg_fdw_import.dual (dummy text) SERVER orcl OPTIONS(schema 'SYS', table 'DUAL', readonly 'true')"));
                        if conn.execute(text(f"select dummy from ora2pg_fdw_import.dual")).fetchone():
                            self.logger.info(f"Connection to Oracle Foreign Wrapper succeed -  ora2pg_fdw_import") 
                            return True
                        else:
                            self.logger.info(f"Connection to Oracle Foreign Wrapper failed -  ora2pg_fdw_import") 
                            return False
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)          
        except Exception as e:
            self.logger.error(f"{e.__cause__}")

    def fetch_table_exists(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    result = conn.execute(text(f"SELECT STRING_AGG(c.relname , ',' ORDER BY null) as exists_table_list FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r','s','') AND n.nspname !~ '^pg_toast' AND n.nspname ~ '^{pg_schema.lower()}$'")).fetchone()[0]
                    if result:
                        return result
                    else:
                        #Intentionally kept None to check at later stage
                        return None
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)  
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
        
    def validate_postgres(self,project_name):
        # username,password,host,port,dbname,pg_schema = self.fetch_pg_cred(project_name)
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                try:
                    conn.execute(text("SELECT version()"))
                    return True
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)  
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False

    def pg_user(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                query = """SELECT true FROM pg_catalog.pg_roles r
                    WHERE r.rolname OPERATOR(pg_catalog.~) '^(<<pg_user>>)$' COLLATE pg_catalog.default"""
                replace_value = query.replace("<<pg_user>>", pg_schema)
                try:
                    result = conn.execute(text(replace_value)).fetchone()
                    if result:
                        return True, pg_schema
                    else:
                        return False, pg_schema
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False)                
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False

    def pg_version(self,project_name):
        try:
            if self.fetch_pg_cred(project_name):
                conn,engine = self.connect_to_postgres(username,password,host,port,dbname,pg_schema)
                query = r"select replace(substr(version(),1,13),'PostgreSQL','')::integer as pgversion"
                try:
                    result = conn.execute(text(query)).fetchone()
                    if not result is None and len(result) > 0:
                        return result[0]
                except Exception as e:
                    self.logger.error(f"{e.__cause__}")
                    return False
                finally:
                    engine.dispose(close=False) 
        except Exception as e:
            self.logger.error(f"{e.__cause__}")
            return False

        


        


            
    
    
