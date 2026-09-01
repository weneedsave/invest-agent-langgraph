import os
import json

def ensure_dir(path:str) -> None:
    os.makedirs(path,exist_ok=True)

def workspace_dir(code:str) -> str:
    return f"workspace/{code}"

def reports_dir() -> str:
    return "reports"

def save_json(data: dict,path: str)->str:
    parent_dir = os.path.dirname(path)
    ensure_dir(parent_dir)#验证存在
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    return path

def read_json(path:str) -> str:
    #读取文件并返回解析后的对象
    with open(path,"r",encoding="utf-8") as f :
        return json.load(f)