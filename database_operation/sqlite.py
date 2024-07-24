import sqlite3
import pandas as pd
from dcgmigrator_core.logging_operation import HandleLogging
from os_operation.os_handling import DirectoryPath

class SqliteDatabaseManagement:
    def __init__(self, project_name):
        self.project_name = project_name
        self.database_path = DirectoryPath(self.project_name)
        log_instance = HandleLogging(self.project_name)
        self.logger = log_instance.handle_log()

    def __enter__(self):
        
        db_path = self.database_path.sqlite_database_path()
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        return self,self.conn

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_tb is None:
            self.conn.commit()
        else:
            self.conn.rollback()     
        self.conn.close()

    def _table(self): 
        try:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS dcg_mig_projects (
                           project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                           project_name TEXT UNIQUE,
                           date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		                   status text,
                           source TEXT,
                           target TEXT
                           );""")
    
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS ora2pg_config_details (
                           project_id INTEGER NOT NULL,
                           key TEXT NOT NULL,
                           value TEXT,
                           date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           PRIMARY KEY (project_id,key)
                           FOREIGN KEY (project_id) REFERENCES dcg_mig_projects (project_id)
                            );""")
            return True
        except Exception as e:
            raise e
   
    def _insert_project(self,project_name, source, target):
        try:
            self.cursor.execute("INSERT INTO dcg_mig_projects (project_name, source, target) VALUES (?,?,?)", (project_name, source, target))
            return True
        except Exception as e:
            raise e
            
    def _remove_project(self,project_name):
        try:
            self.cursor.executescript(f"""DELETE FROM ora2pg_config_details WHERE project_id IN (SELECT project_id FROM dcg_mig_projects WHERE lower(project_name) = lower('{project_name}'));              
            DELETE FROM dcg_mig_projects WHERE lower(project_name) = lower('{project_name}');""")
            return True
        except Exception as e:
            self.logger.error(f"Unable to remove project details from sqlite\n{e}")
            return False
    
    def  _insert_ora2pgconfig_content(self, project_name, key, value):
        try:
            self.cursor.executescript(f"""
            update ora2pg_config_details set value='{value}' where key=upper('{key}') and project_id = (select project_id from dcg_mig_projects where project_name=lower('{project_name}')); 
            INSERT OR IGNORE INTO ora2pg_config_details(project_id, key, value) SELECT project_id, upper('{key}'),'{value}' FROM dcg_mig_projects WHERE lower(project_name) = lower('{project_name}');
            """
            )
        except Exception as e:
            self.logger.error(f"Unable to Upsert config content for project - {project_name}, Key - {key} \n{e}")

    def _insert_ora2pgconfig_bulk(self, project_name, configdata):
        try:
            self.cursor.executemany("INSERT INTO ora2pg_config_details (project_id, key, value) select (SELECT project_id FROM dcg_mig_projects WHERE project_name = :project_name) as project_id , :key, :value", (configdata))
        except Exception as e:
            self.logger.error(f"Unable to insert bulk config content for project - {project_name} from sqlite\n{e}")
        
    def _refresh_ora2pgconfig_content(self, project_name):
        try:
            self.cursor.execute("select key , value from ora2pg_config_details where project_id in (SELECT project_id FROM dcg_mig_projects WHERE project_name = :project_name) order by date_created asc", (project_name,))
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Unable to refresh config from sqlite\n{e}")

    def _refresh_ora2pgconfig_content_conversion(self, project_name):
        try:
            self.cursor.execute("select key , value from ora2pg_config_details where project_id in (SELECT project_id FROM dcg_mig_projects WHERE project_name = :project_name) and key not in ('PG_DSN','PG_PWD','PG_USER') order by date_created asc", (project_name,))
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Unable to refresh config content conversion from sqlite\n{e}")

    def _fetch_property_ora2pgconfig(self, project_name, key):
        try:
            self.cursor.execute("select value from ora2pg_config_details where lower(key) = lower(?) and project_id in (SELECT project_id FROM dcg_mig_projects WHERE lower(project_name) = lower(?))", (key,project_name))
            return self.cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Unable to fetch property of config from sqlite\n{e}")
    
    def _fetch_oracle_connection(self, project_name):
        try:
            self.cursor.execute("select key,value from ora2pg_config_details where project_id = (select project_id from dcg_mig_projects where lower(project_name)= lower(?)) and UPPER(key) in ('ORACLE_DSN','ORACLE_USER','ORACLE_PWD','ORA_SCHEMA')", (project_name,))
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Unable to fetch oracle connection from sqlite\n{e}")
            
    def _fetch_postgres_connection(self, project_name):
        try:
            self.cursor.execute("select key,value from ora2pg_config_details where project_id = (select project_id from dcg_mig_projects where lower(project_name)= lower(?)) and UPPER(key) in ('PG_DSN','PG_USER','PG_PWD','PG_SCHEMA')", (project_name,))
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Unable to fetch postres connection from sqlite\n{e}")
            
    def _validate_project(self,project_name):
        try:
            self.cursor.execute(f"SELECT 1 FROM dcg_mig_projects WHERE lower(project_name) = lower(?)", (project_name,))
            data =  self.cursor.fetchall()
            if not data is None and len(data) > 0:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Unable to validate project from sqlite\n{e}")
            return False

    def _validate_source_connection(self,project_name):
        try:
            self.cursor.execute(f"SELECT 1 FROM (SELECT CASE WHEN COUNT(1) = 4 THEN 1 ELSE 0 END ALL_PG_KEY_EXISTS FROM ora2pg_config_details WHERE project_id = (SELECT project_id FROM dcg_mig_projects WHERE lower(project_name) = lower(?)) AND UPPER(key) in ('ORACLE_USER','ORACLE_PWD','ORACLE_DSN','ORA_SCHEMA'))", (project_name,))
            data =  self.cursor.fetchall()
            if not data is None and len(data) > 0:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Unable to validate source connection from sqlite\n{e}")
            return False

    def _validate_target_connection(self,project_name):
        try:
            self.cursor.execute(f"SELECT 1 FROM (SELECT CASE WHEN COUNT(1) = 4 THEN 1 ELSE 0 END ALL_PG_KEY_EXISTS FROM ora2pg_config_details WHERE project_id = (SELECT project_id FROM dcg_mig_projects WHERE lower(project_name) = lower(?)) AND UPPER(key) IN ('PG_DSN','PG_USER','PG_PWD','PG_SCHEMA')) where ALL_PG_KEY_EXISTS", (project_name,))
            data =  self.cursor.fetchall()
            if not data is None and len(data) > 0:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error occured in SQLite for fetching target connection details- {e}")

    def _update_project_status(self,status,project_name):
        try:
            self.cursor.execute(f"update dcg_mig_projects set status = ? WHERE lower(project_name) = lower(?)", (status,project_name,))
            return True
        except Exception as e:
            self.logger.error(f"Unable to update project status from sqlite\n{e}")
            return False
            
    def _fetch_status(self,project_name):
        try:
            self.cursor.execute("SELECT status FROM dcg_mig_projects WHERE lower(project_name) = lower(?)", (project_name,))
            data = self.cursor.fetchone()[0]
            if not data is None and len(data) > 0:
                return data
            else:
                return ""
        except Exception as e:
            self.logger.error(f"Unable to fetch project status from sqlite\n{e}")
            
    def _fetch_project(self,project_name):
        try:
            self.cursor.execute("SELECT project_name, date_created, status, source, target FROM dcg_mig_projects WHERE lower(project_name) = lower(IFNULL(?, project_name)) order by date_created desc", (project_name,))        
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Unable to fetch project from sqlite\n{e}")
    
    def _remove_config(self,project_name,key):
        try:
            self.cursor.execute("DELETE FROM ora2pg_config_details WHERE (project_id = (select project_id  from dcg_mig_projects where lower(project_name)= lower(?))) and upper(key) = ? ", (project_name,key,))
            return True
        except Exception as e:
            self.logger.error(f"Unable to remove config from sqlite\n{e}")
            return False

    def _fetch_stop_error(self,project_name):
        try:
            self.cursor.execute("SELECT value FROM ora2pg_config_details WHERE (project_id = (SELECT project_id FROM dcg_mig_projects WHERE lower(project_name) = lower(?) AND key = 'STOP_ON_ERROR'))", (project_name,))
            data = self.cursor.fetchone()[0]
            if not data is None and len(data) > 0: 
                return data
            else:
                self.logger.error(f"Unable to fetch STOP_ON_ERROR config from sqlite\n")
                raise Exception("Unable to fetch STOP_ON_ERROR config from sqlite") 
        except Exception as e:
            self.logger.error(f"Unable to fetch STOP_ON_ERROR config from sqlite\n{e}")
            
    def _show_config_jsonarray(self,project_name):
        try:
            self.cursor.execute("select json_group_array(json_object(key ,value)) AS result from ora2pg_config_details where project_id in (SELECT project_id FROM dcg_mig_projects WHERE project_name = :project_name) order by date_created asc", (project_name,))
            data = self.cursor.fetchone()[0]
            if not data is None and len(data) > 0: 
                return data
            else:
                self.logger.error(f"Unable to fetch config from sqlite for project - {project_name}\n")
                raise Exception(f"Unable to fetch config from sqlite for project - {project_name}") 
        except Exception as e:
            self.logger.error(f"Unable to fetch jsonarray config from sqlite\n{e}")

    def create_project(self, project_name, source, target):
        with self:
            try:
                if self._table() and self._insert_project(project_name, source, target):
                    self.logger.info(f"{project_name} project has been created successfully")
                    return True
                else:
                    return False
            except Exception as e:
                self.logger.error(f"{e} \n Project_name : {project_name} \n already exists or internal exception occured!")
       
    def remove_project(self,project_name):
        with self:
            try:
                if self._remove_project(project_name):
                    self.logger.info(f"{project_name} project is removed successfilly")
                    return True
                else:
                    return False
            except Exception as e:
                self.logger.error(f"{e}\n Issue occured in removal of project {project_name}")
                return False
            
    def insert_ora2pgconfig(self,project_name, key, value):
        with self:
            try:
                self._insert_ora2pgconfig_content(project_name, key, value)
                return True
            except sqlite3.IntegrityError as e: 
                self.logger.error(f"{e} \n project_name should be unique")
                return False
            except Exception as e:
                self.logger.error(f"{e} \n Issue occured in SQLite DB operation")
                return False
 
    def insert_ora2pgconfig_many(self,project_name, configdata):
        with self:
            try:
                self._insert_ora2pgconfig_bulk(project_name,configdata)
                return True 
            except sqlite3.IntegrityError as e: 
                self.logger.error(f"{e} \n project_name should be unique")
                return False
            except Exception as e:
                self.logger.error(f"{e} \n Issue occured in SQLite DB operation")
                return False
        
    def refresh_ora2pgconfig(self,project_name):
        with self:
            try:
                result = self._refresh_ora2pgconfig_content(project_name)
                if len(result) > 0:
                    return result
                else:
                    raise Exception(f"Unable to refresh config from sqlite for project - {project_name}")  
            except Exception as e:
               self.logger.error(f"{e} \n No data found for {project_name}")
               return ""
        
    def fetch_oracle_connection(self,project_name):
        with self:
            try:
                result = self._fetch_oracle_connection(project_name)
                if result is not None and len(result) > 0:
                    return result
            except Exception as e:
                self.logger.error(f"{e} \n No data found for {project_name}")

    def fetch_config_value(self,project_name,key):
        with self:
            try:
                value = self._fetch_property_ora2pgconfig(project_name,key)
                if value is not None and len(value) > 0:
                    return value[0]
                else:
                    self.logger.error(f"unable to fetch property {key} from config on project : {project_name}")
                    return ""
            except Exception as e:
                self.logger.error(f"{e} \n No data found for project- {project_name} and key - {key}")
                raise e
        # return value
    def fetch_postgres_connection(self,project_name):
        with self:
            try:
                result = self._fetch_postgres_connection(project_name)
                if result is not None and len(result) >0:
                    return result
                else:
                    self.logger.error(f"unable to fetch postgres connection :  {project_name}")
            except Exception as e:
                self.logger.error(f"{e} \n No data found for {project_name}")

    def show_config(self,project_name):
        try:
            result = self.refresh_ora2pgconfig(project_name)
            if result is not None and len(result) >0:
                for key, value in result:
                    if key != "ORACLE_PWD" and key != "PG_PWD":
                        print(f"{key}   {value}")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"{e}\nUnable to show config for project : {project_name}")

    def generate_config(self,project_name):
        try:
            result = self.refresh_ora2pgconfig(project_name)
            if result is not None and len(result) > 0:    
                result =  [item for item in result if 'ORACLE_PWD' not in item] 
                result =  [item for item in result if 'PG_PWD' not in item] 
                return result
        except Exception as e:
            self.logger.error(f"{e}\nUnable to generate config for project : {project_name}")

    def update_config(self, key, value, project_name):
        with self:
            try:
                self._insert_ora2pgconfig_content(project_name, key, value)
                self.logger.info(f"({key}) has been updated for project : {project_name}")
                return True
            except Exception as e:
                self.logger.error(f"{e} \n Issue occured in DB operation")

    def validate_project(self,project_name):
        with self:
            try:
                if self._validate_project(project_name):
                    return True
                else:
                    return False
            except Exception as e:
                self.logger.error(f"{e} \n Issue occured in DB operation")
      
    def update_project_status(self,status,project_name):
        with self:
            try:
                if self._update_project_status(status,project_name):
                    return True
            except Exception as e:
                self.logger.error(f"{e} \n Issue occured in DB operation")
                return False

    def fetch_status(self,project_name):
        with self:
            try:
                result = self._fetch_status(project_name)
                if result is not None and len(result) > 0:
                    return result
                else:
                    self.logger.error(f"Status for project : {project_name} does not exist")
            except Exception as e:
                self.logger.error(f"{e} \n Issue occured in DB operation")
    
    def fetch_project(self,project_name):
        with self:
            try:
                result = self._fetch_project(project_name)
                if result is not None and len(result) >0:
                    df = pd.DataFrame(result, columns= [column[0] for column in self.cursor.description])
                    if len(df.index)!=0:
                        print(type(df))
                        return df       
                else:
                    self.logger.error(f"Migration project {project_name} does not exists")
            except Exception as e:
                raise e
                
    def remove_config(self,project_name,key):
        with self:
            try:
                if self._remove_config(project_name,key.upper()):
                    self.logger.info(f"({key}) has been removed from project : {project_name}")
                else:
                    self.logger.error(f"Unable to remove {key}")
            except Exception as e:
                raise e
            
    def fetch_stop_error(self,project_name):
        with self:
            try:
                result = self._fetch_stop_error(project_name)
                if result is not None and len(result) > 0:
                    return result
                else:
                    self.logger.error(f"STOP_ON_ERROR flag does not exists in config of project : {project_name}")
            except Exception as e:
                raise e
        
    def show_config_jsonarray(self,project_name):
        with self:
            try: 
                result = self._show_config_jsonarray(project_name)
                if result is not None and len(result) > 0:
                    return result
                else:
                    self.logger.error(f"Unable to create jsonarray of project details : {project_name}")
            except Exception as e:
                raise e
        
    def validate_source_connection(self, project_name):
        with self:
            try:
                if self._validate_source_connection(self,project_name):
                    return True
                else:
                    return False
            except Exception as e:
                raise e

    def validate_target_connection(self,project_name):
        with self:
            try:
                if self._validate_target_connection(project_name):
                    return True
                else:
                    return False
            except Exception as e:
                raise e


            


    







        
    
        

                
        





    


        




