import os
from invest_agent.vfs.filesystem import reports_dir
def report_full(state: dict) -> dict:
    code = state["code"]
    metrics = state["metrics"]
    peers = state["peers"]
    #拼接markdown文本
    lines = [
        f"# {code} 投资简报",
        "",
        "## 财务指标",

    ]
    for k,v in metrics.items():
        lines.append(f"- {k}: {v}")
    lines += ["","## 同业对比"]
    for p in peers:
        lines.append(f"- {p['name']}: ROE {p['roe']}")
    content = "\n".join(lines)

    #写入文件
    d = reports_dir()
    path = f"{d}/{code}.md"
    os.makedirs(d,exist_ok = True) #创建文件夹使用
    with open(path,"w",encoding="utf-8") as f:
        f.write(content)

    print(f"[report_full] 报告已生成: {path}")
    return {"report_path": path}
def report_bank(state:dict)-> dict:
    code = state["code"]
    metrics = state["metrics"]
    peers = state["peers"]
    lines = [
        f"# {code} 投资简报",
        "",
        "## 财务指标",
    ]
    for k, v in metrics.items():
        if v is not None:
            lines.append(f"- {k}: {v}")

    lines += ["", "> 注：银行股无营业成本，毛利率不适用。", ""]

    lines += [
        "## 同业对比",
    ]
    for p in peers:
        lines.append(f"- {p['name']}:ROE {p['roe']}")
    content = "\n".join(lines)
    d = reports_dir()
    path = f"{d}/{code}.md"
    os.makedirs(d,exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        f.write(content)

    print(f"[report_bank] 报告已生成: {path}")
    return {"report_path": path}

