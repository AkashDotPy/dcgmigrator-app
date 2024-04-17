from fastapi import FastAPI
from pydantic import BaseModel
from wrapper import DcgWrapper
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateProject(BaseModel):
    project_name : str
    source : str
    target : str

class CreateSource(BaseModel):
    project_name : str
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

@app.post("/createProject")
async def create_project(requestBody : CreateProject):
    project_name = requestBody.project_name
    source = requestBody.source
    target = requestBody.target
    inst = DcgWrapper(project_name)
    data = inst.create_project_wrapper(project_name, source, target)
    return data

@app.post("/createSource")
async def create_source(requestBody : CreateSource):
    project_name = requestBody.project_name
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


@app.get("/showproject")
async def show_project(project_name):
    inst = DcgWrapper(project_name)
    data = inst.show_project_wrapper(project_name)

    df1 = data.to_json(orient='records') 
    new_df = json.loads(df1)

    return new_df

@app.get("/projectname")
async def project_name(project_name):
    wrapper_inst = DcgWrapper(project_name)
    data = wrapper_inst.show_project_wrapper(project_name)
    return data

@app.get("/showconfig")
async def show_config(project_name):
    wrapper_inst = DcgWrapper("testhr")

    data = wrapper_inst.show_config_wrapper("testhr")
    data_1 = json.loads(data)
    print(data_1)

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