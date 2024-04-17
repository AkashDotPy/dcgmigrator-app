from database_operation.oracle import OracleDatabaseManagement
from dcgmigrator_plus.extension_plus import Extention

class Plus:

    def __init__(self,project_name):
        self.project_name = project_name
        self.ora_instance = OracleDatabaseManagement(self.project_name)
        self.ext_inst = Extention(self.project_name)
        
    def modify_type(self,project_name):
        if self.ora_instance.number_modify_type(project_name):
            return True
        else:
            return False
    
    def extension(self,project_name):
        if self.ext_inst.extention_plus(project_name):
            return True
        else: 
            return False
    
    def extension_command(self,project_name):
        return self.ext_inst.extension_command(project_name)

    def oracle_fdw(self,project_name):
        self.ext_inst.oracle_fdw_plus(project_name)
        return True


        

    
 
        



