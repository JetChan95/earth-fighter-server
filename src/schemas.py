# 定义请求体模型
from pydantic import BaseModel, Field


class LoginModel(BaseModel):
    username: str
    password: str

class UserModel(BaseModel):
    user_id: int
    username: str
    password: str
    register_time: str

class UserPath(BaseModel):
    u_id: int = Field(..., description = '用户id')

class UserRenameModel(BaseModel):
    username: str = Field(..., description='用户名')

class OrganizationModel(BaseModel):
    c_id: int = Field(description = '组织ID')
    c_name: str = Field(description = '组织名称')
    c_type: str = Field(description = '组织类型')
    invite_code: str = Field(description = '邀请码')

class OrgPath(BaseModel):
    c_id: int = Field(..., description = '组织id')
