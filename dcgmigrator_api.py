from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from wrapper import DcgWrapper
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional,Dict, List, Union
import json
from database_operation.sqlite import SqliteDatabaseManagement
from os_operation.os_handling import DirectoryPath
from database_operation.postgres import PostgresDatabase


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ProjectName(BaseModel):
    project_name : Optional[str] = None

class CreateProject(BaseModel):
    project_name : str
    source : str
    target : str

class RemoveProject(BaseModel):
    project_name: str
    remove_file: bool = False
    drop_target_schema: bool = False

class CreateSource(BaseModel):
    project_name : str
    tns_connection : Optional[str] = None
    home : str
    host : str
    service_name : str
    port : str
    user : str
    password : str
    ora_schema : str

class CreateTarget(BaseModel):
    project_name : str
    pg_dbname : str
    pg_host : str
    pg_port : str
    pg_user : str
    pg_password : str
    input_pg_version : str

source_options = ["Oracle"]
target_options = ["PostgreSQL"]

@app.post("/createProject")
async def create_project(requestBody: Union[CreateProject, None] = None, fetch_options: bool = Query(False)):
    if fetch_options:
        return {
            "sources": source_options,
            "targets": target_options
        }
    elif requestBody:
        project_name = requestBody.project_name
        source = requestBody.source
        target = requestBody.target
        inst = DcgWrapper(project_name)
        data = inst.create_project_wrapper(project_name, source, target)
        return data

    else:
        raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/removeproject")
async def remove_project(requestBody : RemoveProject):
    project_name = requestBody.project_name
    sqlite_instance = SqliteDatabaseManagement(project_name)
    os_inst = DirectoryPath(project_name)
    pg_inst = PostgresDatabase(project_name)

    if requestBody.remove_file and os_inst.remove_project_dir(project_name):
        return {f"Project name - {project_name} related all generated files are removed"}

    if requestBody.drop_target_schema and pg_inst.postgres_drop_schema(project_name):
        return {f"Project name - {project_name} target schema is dropped"}

    sqlite_instance.remove_project(project_name)
    return {"message": f"Project {project_name} removed successfully"}


@app.get("/projectname")
async def project_name(project_name=None):
    wrapper_inst = DcgWrapper(project_name)
    projectname = wrapper_inst.show_projectname_wrapper(project_name)
    print(project_name)
    return {"project_name" : projectname}

@app.post("/createSource")
async def create_source(requestBody : CreateSource):
    project_name = requestBody.project_name
    tns_connection = requestBody.tns_connection
    home = requestBody.home
    host = requestBody.host
    service_name = requestBody.service_name
    port = requestBody.port
    user = requestBody.user
    password = requestBody.password
    ora_schema = requestBody.ora_schema
    inst = DcgWrapper(project_name)
    data = inst.create_source_wrapper(project_name, home, host, service_name,port,user,password,ora_schema)
    return data

@app.post("/createTarget")
async def create_target(requestBody : CreateTarget):
    project_name = requestBody.project_name
    pg_dbname = requestBody.pg_dbname
    pg_host = requestBody.pg_host
    pg_port = requestBody.pg_port
    pg_user = requestBody.pg_user
    pg_password = requestBody.pg_password
    input_pg_version = requestBody.input_pg_version
    inst = DcgWrapper(project_name)
    data = inst.create_target_wrapper(project_name,pg_dbname,pg_host,pg_port,pg_user,pg_password,input_pg_version)
    return data

@app.get("/listProjects")
async def show_project(project_name=None):
    inst = DcgWrapper(project_name)
    data = inst.show_project_wrapper(project_name)
    df1 = data.to_json(orient='records') 
    new_df = json.loads(df1)
    return new_df

@app.get("/showconfig")
async def show_config(project_name):
    wrapper_inst = DcgWrapper(project_name)
    data = wrapper_inst.show_config_wrapper("testhr")
    data_1 = json.loads(data)
    return data_1

@app.get("/showschema")
async def show_schema():
    wrapper_inst = DcgWrapper("testhr")

    result = wrapper_inst.show_schema_wrapper("testhr")
    print(result)
    
    return result

@app.get("/showcolumn")
async def show_column():
    wrapper_inst = DcgWrapper("testhr")

    result = wrapper_inst.show_column_wrapper("testhr")
    # data_1 = json.loads(result)
    return result

@app.get("/showtable")
async def show_table():
    wrapper_inst = DcgWrapper("testhr")

    result = wrapper_inst.show_table_wrapper("testhr")
    # data_1 = json.loads(result)
    return result