"""
Day 13 — 双框架对比：HelloAgents 风格 vs LangGraph 风格

【今日目标】
让 mini_react_agent (HelloAgents 风格) 和 langgraph_hello (LangGraph 风格)
跑同一个问题，把差异变成数据，为 Day 14 博客准备素材。

【统一问题】
"北京和上海今天哪个更热？热多少度？再算一下这个温差的 3 倍是多少？"

→ 这个问题需要 3 次工具调用：
   get_weather(北京) + get_weather(上海) + calculate(...)
→ 区别度高，能体现 ReAct 的多步推理能力

【3 个关卡】
- 关卡 1: 跑两版本，收集 metrics（行数/耗时/工具调用次数/迭代次数）
- 关卡 2: 填对比表（在 day13-compare.md 里）
- 关卡 3: 回答 3 个分析题（写进笔记）

【为什么用同一个 question】
科学的对比要控制变量。Day 11/12 用过的"北京温度"只调一次工具，区分不出来。
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 两版的代码都在同目录，直接 import
from mini_react_agent import MiniReActAgent
from langgraph_hello import build_react_graph, SYSTEM_PROMPT, TOOLS


# ============================================================
# 统一问题
# ============================================================
QUESTION = "北京和上海今天哪个更热？热多少度？再算一下这个温差的 3 倍是多少？"


# ============================================================
# 关卡 1：跑两版，收集 metrics
# ============================================================

def run_hello_agents_style():
    """跑 HelloAgents 风格（MiniReActAgent）
    
    返回 dict: {
        "framework": "HelloAgents",
        "elapsed_sec": float,
        "final_answer": str,
        "tool_calls": int,        # 调用工具次数
        "iterations": int,        # ReAct 循环跑了几轮
        "total_messages": int,    # 最终 messages 总条数
        "code_lines": int,        # 框架代码行数（粗略指标）
    }
    """
    # TODO: 实现这个函数
    # 提示：
    # 1. 创建 agent = MiniReActAgent(max_iterations=8)
    # 2. 记录 time.time() 前后差
    # 3. 调 agent.run(QUESTION) 拿到 final_answer
    # 4. tool_calls / iterations / total_messages 需要从 agent 里挖
    #    → 当前 MiniReActAgent 的 messages 是 run() 内部的局部变量
    #    → 你可能需要把它改成 self.messages，或让 run() 同时返回 messages
    #    → 选最小改动方案
    start_time = time.time()
    agent = MiniReActAgent(max_iterations=8)
    final_answer = agent.run(QUESTION)
    messages = agent.messages
    elapsed_sec = time.time() - start_time
    tools_call = len([m for m in messages if m["role"] == "user" and m["content"].startswith("Observation:")])
    return {
        "framework": "HelloAgents",
        "elapsed_sec": elapsed_sec,
        "final_answer": final_answer,
        "tool_calls": tools_call,
        "iterations": tools_call,
        "total_messages": len(messages),
        "code_lines": count_code_lines("mini_react_agent.py", 109, 204),
    }

tools_desc = "\n".join(f"- {name}: {desc}" for name, (fn, desc) in TOOLS.items())
system_prompt = SYSTEM_PROMPT.format(tools_desc=tools_desc)
def run_langgraph_style():
    """跑 LangGraph 风格（build_react_graph 编译出的 app）
    
    返回 dict（同 run_hello_agents_style 的字段）
    """
    # TODO: 实现这个函数
    # 提示：
    # 1. app = build_react_graph()
    # 2. 准备 initial state（参考 langgraph_hello.test_level3）
    #    - messages: [system + user]
    #    - iteration: 0
    #    - final_answer: ""
    # 3. result = app.invoke(initial)，拿 result["final_answer"]
    # 4. tool_calls = result 里 "Observation:" 开头的 user 消息数
    # 5. iterations = result["iteration"]
    # 6. total_messages = len(result["messages"])
    start_time = time.time()
    app = build_react_graph()
    result = app.invoke({"messages": [{"role":"system","content":system_prompt},{"role":"user","content":QUESTION}],
                "iteration": 0,
                "final_answer": ""})
    elapsed_sec = time.time() - start_time
    tools_call = len([m for m in result["messages"] if m["role"] == "user" and  "Observation" in m["content"]])
    return {
        "framework": "LangGraph",
        "elapsed_sec": elapsed_sec,
        "final_answer": result["final_answer"],
        "tool_calls": tools_call,
        "iterations": result["iteration"],
        "total_messages": len(result["messages"]),
        "code_lines": count_code_lines("langgraph_hello.py", 193, 282),
    }


def count_code_lines(filepath: str, start: int = 1, end: int = None) -> int:
    """数指定行范围内的有效代码行（排除空行和纯注释）"""
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    if end is None:
        end = len(lines)
    selected = lines[start - 1 : end]
    return sum(
        1 for ln in selected
        if ln.strip() and not ln.strip().startswith("#")
    )


# ============================================================
# 关卡 2：并排打印对比表
# ============================================================

def print_comparison(result_a: dict, result_b: dict):
    """打印 markdown 友好的对比表，可以直接拷进博客"""
    print("\n" + "=" * 70)
    print(f"问题：{QUESTION}")
    print("=" * 70)
    
    rows = [
        ("框架",         "framework"),
        ("代码行数",     "code_lines"),
        ("耗时（秒）",   "elapsed_sec"),
        ("ReAct 迭代轮数", "iterations"),
        ("工具调用次数", "tool_calls"),
        ("最终 messages", "total_messages"),
        ("最终答案",     "final_answer"),
    ]
    
    # 表头
    print(f"\n| 维度 | {result_a['framework']} | {result_b['framework']} |")
    print(f"|---|---|---|")
    for label, key in rows:
        if key == "framework":
            continue
        va = result_a.get(key, "?")
        vb = result_b.get(key, "?")
        if isinstance(va, float):
            va = f"{va:.2f}"
        if isinstance(vb, float):
            vb = f"{vb:.2f}"
        print(f"| {label} | {va} | {vb} |")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Day 13: 双框架对比开始")
    print("=" * 70)
    
    print("\n>>> 跑 HelloAgents 风格...")
    result_a = run_hello_agents_style()
    
    print("\n>>> 跑 LangGraph 风格...")
    result_b = run_langgraph_style()
    
    print_comparison(result_a, result_b)


# ============================================================
# 关卡 3：跑完后回答这 3 题（答案写进 day13-compare.md）
# ============================================================
# Q1. 同一问题、同一工具，两框架的最终答案一致吗？如果不一致，原因是什么？
#     如果一致，能说明什么？
# 
# Q2. 看你写 run_langgraph_style 时——为了拿 "tool_calls/iterations/messages" 这些指标，
#     是不是几乎不用动脑（result 字典里都有）？
#     而 run_hello_agents_style 你大概率得改 MiniReActAgent 暴露内部状态。
#     这个"暴露内部状态的成本差异"对应两个框架的什么设计哲学？
#
# Q3. 如果让你把当前的 mini_react_agent.py 加上"重启后能恢复对话"的能力，
#     大概要改多少行代码？LangGraph 版本要改多少？
#     → 这个数字差就是 Day 14 博客的最大卖点。
