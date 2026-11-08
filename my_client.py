# my_client.py
# A small MCP client: it starts the server, asks what tools it has,
# then uses predict_both on every test patient.
import asyncio

from agents.mcp import MCPServerStdio
from mcp_client_demo import params, call   # reuse the demo's connection settings


async def main():
    async with MCPServerStdio(params=params, client_session_timeout_seconds=120) as server:
        # 1. Ask the server what it can do (this is MCP's "tools/list")
        tools = await server.list_tools()
        print(f"The server offers {len(tools)} tools:")
        for tool in tools:
            print("  -", tool.name)

        # 2. Make sure the models are trained
        await call(server, "train_models", {"request_id": "hw-train"})

        # 3. Check every test patient with your new tool (this is MCP's "tools/call")
        disagreements = []
        for i in range(114):
            sample = await call(server, "get_sample_input", {"index": i, "request_id": f"hw-sample-{i}"})
            result = await call(server, "predict_both", {
                "input_data": sample["input_data"],
                "request_id": f"hw-both-{i}",
            })
            if not result["models_agree"]:
                disagreements.append(i)
                print(f"Patient {i}: true = {sample['true_class']}, "
                      f"logistic regression = {result['logistic_regression']}, knn = {result['knn']}")

        print(f"\nThe models disagree on {len(disagreements)} of 114 test patients.")


asyncio.run(main())