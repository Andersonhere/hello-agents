"""
Day 12 — LangGraph 进阶：Checkpointer 持久化 + Time Travel

【学习目标】
- 理解 thread_id 是什么、为什么需要它
- MemorySaver：用 thread_id 在同进程内保持多轮 state
- SqliteSaver：state 落盘，重启进程后能恢复
- get_state_history + checkpoint_id：回看历史、从某一步分叉重跑

【3 关卡】
- 关卡 1：MemorySaver，同一 thread_id 跨 invoke 累加状态
- 关卡 2：SqliteSaver，杀进程后用同 thread_id 恢复
- 关卡 3：Time Travel，从历史 checkpoint 分叉

【复用】
- 直接复用 Day 11 的 build_react_graph，但 compile 时传 checkpointer
- 复用 ReActState / call_llm_node / call_tool_node / should_continue

【新概念速记】
- thread_id：一个独立的"会话"。同一 thread 内的多次 invoke 共享 state
- checkpoint_id：thread 内每一步的快照 ID（每次节点执行后框架自动写入）
- config = {"configurable": {"thread_id": "xxx", "checkpoint_id": "yyy"}}
  - 只给 thread_id：从最新 checkpoint 继续
  - 同时给 checkpoint_id：从指定历史点回放/分叉
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 复用 Day 11 已经写好的组件
from langgraph_hello import (
    ReActState,
    call_llm_node,
    call_tool_node,
    should_continue,
    SYSTEM_PROMPT,
    TOOLS,
)
from langgraph.graph import StateGraph, START, END


# ============================================================
# 关卡 1：MemorySaver — 内存版 checkpointer
# ============================================================
"""
【任务】
1. 从 langgraph.checkpoint.memory 导入 MemorySaver
2. 写 build_graph_with_memory(checkpointer)，编译时 graph.compile(checkpointer=...)
3. 用同一个 thread_id 连续 invoke 两次：
   - 第 1 次问"北京今天温度"
   - 第 2 次问"上海呢"  ← 这里只问"上海呢"，看 LLM 能否凭借 messages 历史推断出"温度"
4. 打印两次 invoke 后的 messages 长度，确认第 2 次是在第 1 次基础上累加的

【对比实验】
- 不传 checkpointer 时，第 2 次 invoke 的 state 是从零开始（messages 只有这次的 system+user）
- 传了 checkpointer 后，第 2 次 invoke 自动加载上次 state，messages 是累加的

【提示】
- invoke 时第二个参数：app.invoke(state, config={"configurable": {"thread_id": "user-001"}})
- 第一次 invoke 时传完整初始 state（system + user），第二次只传 {"messages": [新 user 消息]}
"""

from langgraph.checkpoint.memory import MemorySaver

# TODO: 关卡 1 —— 在这里实现 build_graph_with_memory + test_level1
def build_graph_with_checkpointer(checkpointer):
    """TODO: 跟 Day 11 build_react_graph 一样，但 compile 时传 checkpointer"""
    graph = StateGraph(ReActState)
    graph.add_node("llm", call_llm_node)
    graph.add_node("tool", call_tool_node)
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", should_continue,{"tool": "tool", "end": END})
    graph.add_edge("tool", "llm")
    return graph.compile(checkpointer)
    
    # TODO: 用 TOOLS 拼出 tools_desc，填入 SYSTEM_PROMPT
tools_desc = "\n".join(f"- {name}: {desc}" for name, (fn, desc) in TOOLS.items())
system_prompt = SYSTEM_PROMPT.format(tools_desc=tools_desc)

def test_level1():
    """TODO: 见上面注释的 4 步
    
    断言：
    - 第 1 次 invoke 后 messages 长度 >= 4（system + user + assistant + ...）
    - 第 2 次 invoke 后 messages 长度 > 第 1 次（说明累加了）
    """
    graph = build_graph_with_checkpointer(MemorySaver())
    #格式化系统提示词

    config = {"configurable": {"thread_id": "user-001"}}
    graph.invoke({                                          # ← dict
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "北京今天温度"},
    ],
    "iteration": 0,
    "final_answer": "",
}, config)
    print("第一次invoke后messages长度:", len(graph.get_state(config).values["messages"]))
    print("messages:", graph.get_state(config).values["messages"])
    graph.invoke({"messages": [{"role": "user", "content": "上海呢"}]}, config)
    print("第二次invoke后messages长度:", len(graph.get_state(config).values["messages"]))
    print("messages:", graph.get_state(config).values["messages"])

# ============================================================
# 关卡 2：SqliteSaver — 落盘版 checkpointer
# ============================================================
"""
【任务】
1. 从 langgraph.checkpoint.sqlite 导入 SqliteSaver
2. 用 SqliteSaver.from_conn_string("learning-plan/code/week2/.day12_checkpoints.db") 
   ← 注意这个返回的是 context manager
3. 在 with 块里 build graph 并 invoke

【验证持久化】
- 模拟"两个进程"：第一次跑 test_level2_part1，存盘后 exit
- 第二次跑 test_level2_part2，用同一个 thread_id 接着问"上海呢"
- 期望：第 2 次能拿到完整 messages 历史

【提示】
- SqliteSaver 是 context manager：with SqliteSaver.from_conn_string("...") as cp: ...
- 也可以手动创建 conn = sqlite3.connect(...) 然后 SqliteSaver(conn)
- 数据库文件路径写到 learning-plan/code/week2/.day12_checkpoints.db（要加到 .gitignore）
"""

# TODO: 关卡 2 —— 实现两个函数，模拟"先存后恢复"两个独立进程
from langgraph.checkpoint.sqlite import SqliteSaver
def test_level2_part1():
    """TODO: 第一次进程：用 thread_id="user-002" 问"北京今天温度"，存盘后退出"""
    with SqliteSaver.from_conn_string(".day12_checkpoints.db") as cp:
        graph = build_graph_with_checkpointer(cp)
        config = {"configurable": {"thread_id": "user-002"}}
        graph.invoke({                                          # ← dict
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "北京今天温度"},
        ],
        "iteration": 0,
        "final_answer": "",
    }, config)
        print("第一次invoke后messages长度:", len(graph.get_state(config).values["messages"]))
        print("messages:", graph.get_state(config).values["messages"])
    pass


def test_level2_part2():
    """TODO: 第二次进程：用同一个 thread_id 问"那上海呢"，期望能拿到上次 messages"""
    with SqliteSaver.from_conn_string(".day12_checkpoints.db") as cp:
        graph = build_graph_with_checkpointer(cp)
        config = {"configurable": {"thread_id": "user-002"}}
        graph.invoke({"messages": [{"role": "user", "content": "那上海呢"}]}, config)
        print("第二次invoke后messages长度:", len(graph.get_state(config).values["messages"]))
        print("messages:", graph.get_state(config).values["messages"])


# ============================================================
# 关卡 3：Time Travel — 历史回放 + 分叉
# ============================================================
"""
【任务】
1. 用关卡 2 的 SqliteSaver，跑一个完整 ReAct 流程拿到 thread_id
2. 用 app.get_state_history(config) 拿到所有 checkpoint
   - 返回 list[StateSnapshot]，每个有 .config, .values, .next, .metadata 等
3. 打印每个 checkpoint 的关键信息：iteration、最新消息 role/content 前 30 字、checkpoint_id
4. 挑"调完工具刚回到 LLM 节点"那一步的 checkpoint_id，分叉重跑：
   - config_fork = {"configurable": {"thread_id": "...", "checkpoint_id": "..."}}
   - app.invoke(None, config_fork) 从这步继续
   - 观察：会生成新的 checkpoint，但原线时间线不受影响

【提示】
- get_state_history 返回**新到旧**的顺序
- 用 list(app.get_state_history(config)) 强制取完
- 分叉时 input 传 None，框架自动从 checkpoint 加载 state
"""

# TODO: 关卡 3 —— 实现 test_level3_time_travel

def test_level3_time_travel():
    """TODO:
    Step 1: 跑一个完整 ReAct 流程
    Step 2: list 所有 history checkpoint，打印
    Step 3: 挑某个 checkpoint_id 分叉重跑
    Step 4: 再 list 历史，应该看到新的分叉 checkpoint
    """
    config = {"configurable": {"thread_id": "user-002"}}
    with SqliteSaver.from_conn_string(".day12_checkpoints.db") as cp:
        graph = build_graph_with_checkpointer(cp)

        # Step 1: 列出所有历史 checkpoint
        history = list(graph.get_state_history(config))
        print(f"总共 {len(history)} 个 checkpoint")
        for i, snap in enumerate(history):
            cid = snap.config["configurable"]["checkpoint_id"]
            msgs = snap.values.get("messages") or []
            last = msgs[-1] if msgs else {}
            print(f"[{i:>2}] cp_id={cid[:8]}.. "
                  f"iter={snap.values.get('iteration')} "
                  f"next={snap.next} "
                  f"last={last.get('role','?')}: {str(last.get('content',''))[:30]}")

        # Step 2: 挑分叉点 —— 找"工具刚返回 Observation、即将进入 llm"那个 cp
        config_fork = None
        for snap in history:
            msgs = snap.values.get("messages") or []
            if not msgs:
                continue
            last = msgs[-1]
            if (snap.next == ("llm",)
                    and last.get("role") == "user"
                    and "Observation:" in last.get("content", "")):
                config_fork = snap.config
                print(f"\n选中分叉点: cp_id={config_fork['configurable']['checkpoint_id'][:8]}..")
                print(f"  当时 messages 数 = {len(msgs)}")
                break

        if config_fork is None:
            print("未找到合适的分叉点")
            return

        # Step 3: 从分叉点重跑（input=None，框架自动从快照加载 state）
        fork = graph.invoke(None, config_fork)
        print(f"\n分叉后 messages 数 = {len(fork['messages'])}")
        print(f"分叉后 final_answer = {fork['final_answer']!r}")

        # Step 4: 看历史是否多出了新分支
        new_history = list(graph.get_state_history(config))
        print(f"\n分叉前历史 = {len(history)}, 分叉后历史 = {len(new_history)}")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    # 用法: python langgraph_checkpoint.py <关卡>
    #   1   → 关卡 1: MemorySaver
    #   2a  → 关卡 2 part1: SqliteSaver 写入
    #   2b  → 关卡 2 part2: SqliteSaver 恢复
    #   3   → 关卡 3: time travel
    funcs = {
        "1":  test_level1,
        "2a": test_level2_part1,
        "2b": test_level2_part2,
        "3":  test_level3_time_travel,
    }
    if len(sys.argv) < 2 or sys.argv[1] not in funcs:
        print(f"用法: python {sys.argv[0]} <{'|'.join(funcs)}>")
        sys.exit(1)
    funcs[sys.argv[1]]()


# ============================================================
# 完成后回答这 4 题（写进笔记）
# ============================================================
# Q1. thread_id 在 LangGraph 里扮演什么角色？为什么不让框架自动生成而要用户传？
# A1. 

# Q2. MemorySaver 和 SqliteSaver 在你写的代码里只差一行，但语义差别巨大。
#     这种"接口同形、实现异化"的设计对应什么编程范式？
# A2. 

# Q3. checkpoint_id 让你能从历史某点"分叉"重跑。这跟 Git 的 commit/branch 模型有什么类比？
#     如果你要做一个 Agent 调试工具，会怎么用这个能力？
# A3. 

# Q4. 持久化以后，state 的字段就必须能被 pickle/json 序列化。
#     如果你的 state 里塞了一个 OpenAI client 对象会怎样？这给你的"节点设计"什么提示？
# A4. 
