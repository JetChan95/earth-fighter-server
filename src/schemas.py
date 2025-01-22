# 定义请求体模型
from pydantic import BaseModel, Field


class LoginModel(BaseModel):
    username: str
    password: str

class UserModel(BaseModel):
    username: str
    password: str

class UserPath(BaseModel):
    u_id: int = Field(..., description = '用户id')

class UserNameModel(BaseModel):
    username: str = Field(..., description='用户名')
    
class UserPasswordModel(BaseModel):
    password: str = Field(..., description='密码')

class OrganizationModel(BaseModel):
    c_id: int = Field(description = '组织ID')
    c_name: str = Field(description = '组织名称')
    c_type: str = Field(description = '组织类型')
    invite_code: str = Field(description = '邀请码')

class OrgPath(BaseModel):
    c_id: int = Field(..., description = '组织id')

class TaskModel(BaseModel):
    task_id: int = Field(description = '任务id')
    task_name: str = Field(description = '任务名称')
    publisher_id: int = Field(description = '创建者id')
    receiver_id: int = Field(description = '接收者id')
    task_state: str = Field(description = '任务状态')
    publish_time: str = Field(description = '发布时间')
    time_limit: int = Field(description = '时间限制')
    completion_time: str = Field(description = '完成时间')
    c_id: int = Field(description = '组织id')
    task_desc: str = Field(description = '任务描述')

class TaskPath(BaseModel):
    task_id: int = Field(..., description = '任务id')
    
class TaskStateModel(BaseModel):
    task_state: str = Field(..., description = '任务状态')
    
class OrgUserModel(BaseModel):
    u_id: int = Field(..., description = '用户id')
    c_id: int = Field(..., description = '组织id')
