import os
def report(state: dict) -> dict:
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
        lines.append(f"- {k}:{v}")
    lines += ["","##同业对比"]
    for p in peers:
        lines.append(f"- {p['name']}: ROE {p['roe']}")
    content = "\n".join(lines)

    #写入文件

    path = f"reports/{code}.md"
    os.makedirs("reports",exist_ok = True) #创建文件夹使用
    with open(path,"w",encoding="utf-8") as f:
        f.write(content)

    print(f"[report] 报告已生成: {path}")
    return {"report_path": path}