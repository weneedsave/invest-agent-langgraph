import sys
from langgraph.checkpoint.sqlite import SqliteSaver
from invest_agent.graph import build_graph

def main() :
    #从命令行读取股票代码
    if len(sys.argv) < 2:
        print("用法: python -m invest_agent.main <股票代码>")
        sys.exit(1)
    code = sys.argv[1]

    #
    with SqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:
        app = build_graph(checkpointer=checkpointer)

        thread_id = f"invest-{code}"

        result = app.invoke(
            {"code":code},
            config={"configurable": {"thread_id": thread_id}}
        )

    print(f"\n===分析完成===")
    print(f"报告路径:{result['report_path']}")

if __name__== "__main__":
    main()