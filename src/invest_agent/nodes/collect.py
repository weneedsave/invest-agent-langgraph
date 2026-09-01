def collect(state: dict) -> dict:
    code = state["code"]
    print(f"[collect] 采集股票 {code} 数据...")
    return {"raw_data_path":f"/workspace/{code}/raw.json"}