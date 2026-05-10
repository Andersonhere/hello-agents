"""
Day 10 手写极简版 ReActAgent —— 骨架提示卡

【规则】
1. 不看 HelloAgents ReActAgent 源码，自己写
2. 总行数 ≤ 80（不含注释和空行）
3. 必须能跑通 main() 里的测试题
4. 跑通后再对比官方 ReActAgent 源码

【写之前先回答这 4 题（默想或写在下面注释里）】
- Q1. ReAct prompt 模板长啥样？三段式 Thought/Action/Observation 怎么组织？
- Q2. 怎么从 LLM 输出里把 Action 提取出来？（正则 / 分隔符）
- Q3. 工具调用结果（Observation）怎么塞回 messages？用什么 role？
- Q4. 什么时候停止循环？（提示：两种终止条件）

A1. 你的回答必须使用Thought和Action两个部分，其中Thought部分用于思考，Action部分用于执行工具调用，finish给出最终答案
A2. 使用正则提取，或者解析json
A3. 使用user role，将工具调用结果作为user role的消息塞回messages
A4. 当出现finish时停止循环，或者达到最大迭代次数时停止循环

【依赖】
- 复用 Day 9 的 OpenAI client + .env 加载方式
- 不引入任何新依赖（不要装 langchain/langgraph）

==============================================================
                     ↓ 在下面动手写 ↓
==============================================================
"""

import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


# ==============================================================
# 1. 工具定义（最简：一个函数 + 一个描述字符串）
# ==============================================================
# TODO: 实现 2 个 mock 工具
def get_weather(city: str) -> str:
    """根据城市返回温度。Mock 数据即可，不用调真 API。"""
    # TODO: 写一个 dict 返回固定温度
    weather_data = {
        "北京": "10°C",
        "上海": "15°C",
        "广州": "20°C",
        "深圳": "25°C",
    }
    return weather_data.get(city, "未知城市")


def calculate(expression: str) -> str:
    """计算数学表达式。提示：可用 eval()，但要 catch 异常。"""
    # TODO
    try:
        return str(eval(expression))
    except:
        return "计算错误"


# 工具注册表：{工具名: (函数, 描述)}
# TODO: 把上面 2 个工具注册进来
TOOLS = {
    "get_weather": (get_weather, "查询城市温度，参数: city (字符串)"),
    "calculate":   (calculate,   "计算数学表达式，参数: expression (字符串)"),
}


# ==============================================================
# 2. ReAct Prompt 模板
# ==============================================================
# TODO: 写一个 system prompt，要点：
#   - 告诉 LLM 它有哪些工具（用 TOOLS 拼接）
#   - 规定输出格式：每轮必须包含 "Thought:" 和 "Action:" 两行
#   - Action 格式约定：Action: 工具名[参数]   或   Action: Finish[最终答案]
#   - 给 1 个示例（few-shot）
SYSTEM_PROMPT = """你是一个会使用工具的智能助手。

# 可用工具
{tools_desc}

# 输出格式（每轮严格遵守）
Thought: [你的思考]
Action: [工具名(参数)]   或者   Finish[最终答案]

# 示例
用户：上海今天比北京冷多少度？
Thought: 我需要分别查上海和北京的温度。
Action: get_weather(上海)
Observation: 上海今天 18 度
Thought: 现在查北京。
Action: get_weather(北京)
Observation: 北京今天 22 度
Thought: 北京比上海高 4 度，所以上海比北京冷 4 度。
Action: Finish[上海比北京冷 4 度]

# 规则
1. 每轮只输出一个 Thought + 一个 Action，不要多
2. 不要自己编造 Observation，等系统返回
3. 拿到足够信息后用 Finish 结束
"""


# ==============================================================
# 3. ReAct Agent 主体
# ==============================================================
class MiniReActAgent:
    """极简 ReActAgent，目标 ≤ 80 行实现"""

    def __init__(self, max_iterations: int = 5):
        # TODO: 初始化 LLM client、model、max_iterations
        self.model = os.getenv("LLM_MODEL_ID")
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            timeout=60
        )
        self.max_iterations = max_iterations
        # TODO: 用 TOOLS 拼出 tools_desc，填入 SYSTEM_PROMPT
        tools_desc = "\n".join(f"- {name}: {desc}" for name, (fn, desc) in TOOLS.items())
        self.system_prompt = SYSTEM_PROMPT.format(tools_desc=tools_desc)

    def _parse_action(self, llm_output: str):
        """
        TODO: 从 LLM 输出里提取 Action
        返回 (tool_name, params) 或 ("finish", final_answer) 或 None
        提示：用正则匹配 'Action: xxx(yyy)' 或 'Action: Finish[zzz]'
        """
        import re
        action_match = re.search(r"Action:\s*(.+)", llm_output)
        if action_match:
            action = action_match.group(1).strip()
            if action.startswith("Finish"):
                return ("finish", action[7:-1].strip())
            else:
                tool_name = action.split("(")[0].strip()
                params = action.split("(")[1].split(")")[0].strip()
                return (tool_name, params)
        return None

    def _execute_tool(self, tool_name: str, params: str) -> str:
        """TODO: 在 TOOLS 里查工具并执行，返回 Observation 字符串"""
        if tool_name not in TOOLS:
            return f"工具 {tool_name} 不存在"
        fn, _desc = TOOLS[tool_name]
        return fn(params)

    def run(self, question: str) -> str:
        """
        TODO: 实现 ReAct 循环
        Step 1: 初始化 messages，包含 system prompt + 用户问题
        Step 2: while 循环 (最多 max_iterations 次):
            - 调 LLM 拿到 response
            - 把 response 加进 messages（assistant role）
            - 解析 Action
            - 如果是 Finish → 返回最终答案
            - 否则执行工具，把 Observation 拼成 user role 加进 messages
        Step 3: 超过迭代上限，返回 "未能在 N 轮内解决"
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]
        
        import time, json
        for i in range(self.max_iterations):
            # 简单重试：网络抖动时最多重试 3 次，指数退避
            for attempt in range(3):
                try:
                    # with_raw_response 拿到底层 HTTP 响应，可读 .text / .headers / .status_code
                    raw = self.client.chat.completions.with_raw_response.create(
                        model=self.model,
                        messages=messages,
                        stop=["Observation:"],
                    )
                    print(f"\n========== 第 {i+1} 轮 RAW Response ==========")
                    print(f"Status: {raw.status_code}")
                    print(f"Body  : {json.dumps(json.loads(raw.text), ensure_ascii=False, indent=2)}")
                    print("=" * 50)
                    response = raw.parse()  # 解析成 ChatCompletion 对象，后面照常用
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"❌ LLM 调用失败，已重试 3 次，放弃")
                        raise
                    wait = 2 ** attempt
                    print(f"⚠️ LLM 调用失败 ({e.__class__.__name__})，{wait}s 后重试...")
                    time.sleep(wait)
            assistant_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})
            
            action = self._parse_action(assistant_message)
            if action is None:
                break
                
            if action[0] == "finish":
                return action[1]
                
            observation = self._execute_tool(action[0], action[1])
            messages.append({"role": "user", "content": f"Observation: {observation}"})
            
        return f"未能在 {self.max_iterations} 轮内解决"


# ==============================================================
# 4. 自测：跑通才算 Day 10 完成
# ==============================================================
def main():
    agent = MiniReActAgent(max_iterations=5)

    # 测试题：必须用到 get_weather + calculate 两个工具
    question = "北京今天的温度乘以 2 等于多少？"
    print(f"问题：{question}\n")
    answer = agent.run(question)
    print(f"\n最终答案：{answer}")


if __name__ == "__main__":
    main()


# ==============================================================
#                完成后回答这 3 个问题（写到笔记里）
# ==============================================================
# Q1. 你的 _parse_action 用的是什么策略？如果 LLM 输出格式略微偏离，会怎样？
# A1. 正则解析，如果偏离了，会出现解析错误

# Q2. 跑测试时 LLM 有没有"自己编 Observation"的情况？你怎么发现的？
# A2. 有，发现方法是打印 messages

# Q3. 对比 Day 9 的 SimpleAgent，ReActAgent 多出来的"循环"本质是什么？
#     用一句话回答：ReAct = SimpleAgent + ___ + ___
# A3. ReAct = SimpleAgent + 思考 + 工具调用
