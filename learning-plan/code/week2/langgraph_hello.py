"""
Day 11 LangGraph Hello World —— 骨架提示卡

【目标】用 LangGraph 实现 3 个递进版本，理解 State / Node / Edge / Conditional Edge

【三道关卡】
关卡 1: 线性 graph (START → hello → world → END)
关卡 2: 加 LLM 节点 (START → ask_llm → END)，state 累积 messages
关卡 3: 条件边 + 循环 (START → call_llm → [tool / END]，tool 节点回连 call_llm)

【写之前先回答】
- Q1. State 和 Day 10 的 messages 有什么区别？
- Q2. 节点函数 return 一个 dict 时，框架怎么处理？（merge 还是 replace？）
- Q3. conditional_edge 返回的字符串是什么？

A1. state是抽象的，messages是具体的
A2. merge
A3. 节点名

==============================================================
关卡 1: 线性 graph（先跑通这个再往下）
==============================================================
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ----- 关卡 1: 线性 graph -----

class HelloState(TypedDict):
    msg: str


def hello_node(state: HelloState) -> dict:
    """TODO: 在 state.msg 后追加 ' hello'，返回 {'msg': 新值}"""
    return {'msg': state['msg'] + ' hello'}


def world_node(state: HelloState) -> dict:
    """TODO: 在 state.msg 后追加 ' world'"""
    return {'msg': state['msg'] + ' world'}


def build_linear_graph():
    """TODO: 4 步建图
    1. graph = StateGraph(HelloState)
    2. add_node 注册 hello_node, world_node（节点名建议小写）
    3. add_edge 连接 START → hello → world → END
    4. return graph.compile()
    """
    graph = StateGraph(HelloState)
    graph.add_node('hello', hello_node)
    graph.add_node('world', world_node)
    graph.add_edge(START, 'hello')
    graph.add_edge('hello', 'world')
    graph.add_edge('world', END)
    return graph.compile()


# ==============================================================
# 关卡 2: 加 LLM 节点
# ==============================================================
"""
【目标】写一个最简单的"问答 graph"：START → ask_llm → END
       理解节点如何复用 LLM client，state 如何承载请求/响应

【写之前先回答】
- Q1. ask_llm_node 应该 return 什么？整个 state 还是只有 answer 字段？
- Q2. LLM client 应该在哪里初始化？节点函数里 vs 模块顶层？哪个好？
- Q3. 如果想让多个节点共享同一个 LLM client，怎么做最优雅？

A1. 
A2. 
A3. 

【提示】
- 复用 Day 10 的 .env 加载方式（load_dotenv + os.getenv）
- LLM client 建议在模块顶层初始化（避免每个节点重复建连接）
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# TODO: 在模块顶层初始化一个 LLM client（复用，所有节点共享）
LLM = OpenAI(api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),)  # 替换成 OpenAI(api_key=..., base_url=...) 实例
MODEL = os.getenv("LLM_MODEL_ID")


class LLMState(TypedDict):
    question: str
    answer: str


def ask_llm_node(state: LLMState) -> dict:
    """TODO: 读 state["question"]，调 LLM，返回 {"answer": llm 回复内容}

    要点：
    - 不要修改 state（坑 3 教训）
    - return 的 dict 只包含 answer 字段（让框架自己 merge）
    - 不需要管 messages 累积（这关只问一次）
    """
    answer = LLM.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": state["question"]}
        ]
    )
    return {"answer": answer.choices[0].message.content}


def build_qa_graph():
    """TODO: START → ask_llm → END"""
    graph = StateGraph(LLMState)
    graph.add_node('answer', ask_llm_node)
    graph.add_edge(START,'answer')
    graph.add_edge('answer', END)
    return graph.compile()


def test_level2():
    app = build_qa_graph()
    result = app.invoke({"question": "用一句话解释什么是 ReAct？", "answer": ""})
    print(f"\n关卡 2 输出:")
    print(f"  问题: {result['question']}")
    print(f"  回答: {result['answer']}")
    assert len(result["answer"]) > 10, "answer 太短，可能没调通 LLM"
    assert result["question"] == "用一句话解释什么是 ReAct？", "question 不应被修改"
    print("✅ 关卡 2 通过\n")


# ==============================================================
# 关卡 3: 用 LangGraph 重写 Day 10 的 ReAct（重头戏）
# ==============================================================
"""
【目标】用 LangGraph 重写 mini_react_agent.py，对标 Day 10 的 80 行手写版

【架构图】
        START
          │
          ▼
      ┌─────────┐
      │ call_llm│◄────────┐
      └────┬────┘         │
           │              │
           ▼              │
      ┌────────────┐      │
      │ should_act?│      │
      └────┬───────┘      │
           │              │
       是  │  否          │
           │              │
      ┌────▼─────┐        │
      │call_tool ├────────┘
      └──────────┘
           │
           ▼ (Finish[...])
          END

【写之前先回答】
- Q1. messages 字段在 State 里要不要用 Annotated[list, add]？为什么？
- Q2. 怎么判断该去 call_tool 还是 END？这个判断函数放在哪里？
- Q3. 怎么防止无限循环？（Day 10 用 max_iterations，LangGraph 怎么做？）

A1. 需要，防止答案覆盖，支持自动追加历史消息
A2. 通过模型返回格式来判断，如果返回的是工具调用格式，则去 call_tool，否则去 END，放在should_continue
A3. 通过配置 max_iterations 来防止无限循环

【约束】
- 复用 Day 10 的 TOOLS、SYSTEM_PROMPT、_parse_action（可以从 mini_react_agent.py import）
- 不要再造轮子，重点体验"画图"取代"写循环"
- 用 RetryPolicy 替代手写重试（坑 2 的改进）
"""

from typing import Annotated
import operator
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从 Day 10 的实现里复用工具和解析逻辑
from mini_react_agent import TOOLS, SYSTEM_PROMPT, MiniReActAgent

# 借用一下 _parse_action（实例方法，绑一个临时实例即可）
_helper = MiniReActAgent.__new__(MiniReActAgent)  # 不调 __init__，只为拿 _parse_action
_parse_action = _helper._parse_action


class ReActState(TypedDict):
    """ReAct 循环的共享状态
    - messages: 累加式，每个节点 return {"messages": [新增的]}，框架自动 append
    - final_answer: Finish[...] 时填入，作为结束标志
    - iteration: 防止无限循环
    """
    messages: Annotated[list, operator.add]  # 关键：用 reducer 实现累加
    final_answer: str
    iteration: int


# TODO: 节点 1 —— 调 LLM
def call_llm_node(state: ReActState) -> dict:
    """读 state["messages"]，调 LLM（带 stop=["Observation:"]），return {"messages": [新 assistant 消息]}
    
    提示：
    - 第一次进来时 messages 为空，需要插入 system + 初始 user question
    - 但用户的 question 应该在 invoke 时就传进 messages（看 test_level3）
    """
    response = LLM.chat.completions.create(
        model=MODEL,
        messages=state["messages"],
        stop=["Observation:"]
    )
    content = response.choices[0].message.content
    # 始终把这条 assistant 消息追加进 messages（保留完整 trace）
    ret = {"messages": [{"role": "assistant", "content": content}]}
    # 命中 Finish[...] 时，额外提取方括号里的纯答案到 final_answer
    m = re.search(r"Finish\[(.*?)\]", content, re.DOTALL)
    if m:
        ret["final_answer"] = m.group(1).strip()
    return ret


# TODO: 节点 2 —— 执行工具
def call_tool_node(state: ReActState) -> dict:
    """从最新的 assistant message 里 _parse_action，执行工具，
    return {"messages": [新 user(Observation) 消息], "iteration": state["iteration"]+1}
    
    提示：
    - 解析失败或拿到 finish 时不该走到这里（路由层已经拦掉）
    - 工具执行也复用 Day 10 的 TOOLS 字典
    """
    last_message = state["messages"][-1]
    action = _parse_action(last_message["content"])
    if action is None:
        raise RuntimeError(f"call_tool_node 被错误调度，最后一条消息无 Action: {last_message['content']!r}")
    tool_name = action[0]
    tool_args = action[1]
    fn, _desc = TOOLS[tool_name]
    observation = fn(tool_args)
    return {"messages": [{"role": "user", "content": f"Observation: {observation}"}], "iteration": state["iteration"] + 1}


# TODO: 路由函数（不是节点，是条件边的判断器）
def should_continue(state: ReActState) -> str:
    """根据最新 assistant message 决定下一步：
    - 包含 Finish[...]  → 返回 "end"
    - 包含 Action: xxx → 返回 "tool"
    - 超过 5 轮迭代    → 返回 "end"
    
    返回的字符串必须是 add_conditional_edges 里 mapping 的 key
    """
    last_message = state["messages"][-1]
    if state["iteration"] >= 5:
        return "end"
    if "Finish[" in last_message["content"]:
        return "end"
    if "Action:" in last_message["content"]:
        return "tool"

    return "end"


def build_react_graph():
    """TODO: 用 4 个 API 建图
    1. StateGraph(ReActState)
    2. add_node 加 call_llm / call_tool
    3. add_edge(START, "llm")
    4. add_conditional_edges("llm", should_continue, {"tool": "tool", "end": END})
    5. add_edge("tool", "llm")   ← 这条边形成循环
    6. compile()
    """
    graph = StateGraph(ReActState)
    graph.add_node("llm", call_llm_node)
    graph.add_node("tool", call_tool_node)
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", should_continue, {"tool": "tool", "end": END})
    graph.add_edge("tool", "llm")
    return graph.compile()


def test_level3():
    app = build_react_graph()
    initial_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "北京今天的温度乘以 2 等于多少？"},
    ]
    result = app.invoke({
        "messages": initial_messages,
        "final_answer": "",
        "iteration": 0,
    })
    print(f"\n关卡 3 输出:")
    print(f"  最终答案: {result['final_answer']}")
    print(f"  迭代轮数: {result['iteration']}")
    print(f"  消息条数: {len(result['messages'])}")
    assert "20" in result["final_answer"], f"期望答案含 20，实际 {result['final_answer']!r}"
    print("✅ 关卡 3 通过\n")


# ==============================================================
# 测试入口
# ==============================================================
def test_level1():
    app = build_linear_graph()
    result = app.invoke({"msg": "say:"})
    print(f"关卡 1 输出: {result}")
    assert result["msg"] == "say: hello world", f"期望 'say: hello world'，实际 {result['msg']!r}"
    print("✅ 关卡 1 通过\n")


if __name__ == "__main__":
    # test_level1()
    # test_level2()
    test_level3()


# ==============================================================
# 完成后回答这 4 个对比题（写到笔记里）
# ==============================================================
# Q1. LangGraph 的 State vs Day 10 的 messages 局部变量，各自痛点？
# A1. state比较黑盒，较难理解。局部变量比较直观，但复用性差。

# Q2. 节点函数签名 (state) -> dict，相比 Day 10 的 run() 方法，复用性如何？
# A2. 节点函数签名 (state) -> dict复用性更好，因为可以被多个节点调用。

# Q3. conditional_edge 相比 if-else，调试时哪个更方便？为什么？
# A3. conditional_edge更方便，因为可以清晰地看到每个条件的执行路径。

# Q4. 用 LangGraph 重写你 Day 10 的 mini_react_agent，会少多少代码？复杂度怎么变？
# A4. 会少很多代码，复杂度会降低。
