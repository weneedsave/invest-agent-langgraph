from typing import TypedDict


class InvestState(TypedDict):
    code: str
    raw_data_path: str | None
    metrics: dict | None
    peers: list[dict] | None
    report_path: str | None