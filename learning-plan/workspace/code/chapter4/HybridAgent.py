"""
组合范式 Agent 设计

设计思路：结合 Plan-and-Solve + ReAct + Reflection 三种范式
1. Plan-and-Solve: 先生成整体计划
2. ReAct: 执行每个步骤（可调用工具）
3. Reflection: 对最终结果进行反思优化

适用场景：复杂的多步骤任务，需要工具交互且对结果质量要求高
"""

import re
import os
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ============================================================================
# LLM 客户端
# ============================================================================

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        self.model = os.getenv("LLM_MODEL_ID")

    def think(self, messages: List[Dict], temperature: float = 0) -> str:
        print(f"🧠 正在调用 {self.model}...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True
        )
        collected = []
        print("✅ 响应: ", end="")
        for chunk in response:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            collected.append(content)
        print()
        return "".join(collected)


# ============================================================================
# 工具定义
# ============================================================================

def get_weather(city: str) -> str:
    """查询天气"""
    import requests
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        data = response.json()
        current = data['current_condition'][0]
        return f"{city}天气：{current['weatherDesc'][0]['value']}，气温{current['temp_C']}°C"
    except Exception as e:
        return f"查询失败：{e}"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        allowed = set('0123456789+-*/(). ')
        if not all(c in allowed for c in expression):
            return "错误：只支持基本数学运算"
        return f"结果：{expression} = {eval(expression)}"
    except Exception as e:
        return f"计算错误：{e}"


def get_time(city: str) -> str:
    """查询时间"""
    import pytz
    tz_map = {
        "北京": "Asia/Shanghai", "上海": "Asia/Shanghai",
        "东京": "Asia/Tokyo", "纽约": "America/New_York", "伦敦": "Europe/London"
    }
    tz = pytz.timezone(tz_map.get(city, "Asia/Shanghai"))
    now = datetime.now(tz)
    return f"{city}当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"


TOOLS = {
    "get_weather": {"func": get_weather, "desc": "查询城市天气。参数：城市名"},
    "calculate": {"func": calculate, "desc": "计算数学表达式。参数：表达式"},
    "get_time": {"func": get_time, "desc": "查询城市时间。参数：城市名"}
}


# ============================================================================
# 提示词模板
# ============================================================================

PLANNER_PROMPT = """
你是一个任务规划专家。请将用户问题分解为清晰的步骤计划。

问题: {question}

请输出步骤列表，格式：
```python
["步骤1", "步骤2", ...]
```
"""

EXECUTOR_PROMPT = """
你是一个执行专家。请根据计划执行当前步骤。

# 原始问题: {question}
# 完整计划: {plan}
# 已完成步骤: {history}
# 当前步骤: {current_step}

可用工具:
{tools}

输出格式：
Thought: [思考过程]
Action: [工具名(参数)] 或 Finish[最终答案]
"""

REFLECTOR_PROMPT = """
你是一个质量评审专家。请评估执行结果的质量。

# 原始问题: {question}
# 执行过程: {trajectory}
# 最终结果: {result}

请评估结果是否正确、完整。如果满意请回复"通过"，否则指出问题。
"""


# ============================================================================
# 组合范式 Agent
# ============================================================================

class HybridAgent:
    """
    组合范式 Agent：Plan → ReAct Execute → Reflect
    """

    def __init__(self, llm: LLMClient, max_steps: int = 5):
        self.llm = llm
        self.max_steps = max_steps

    def run(self, question: str) -> str:
        print(f"\n{'='*60}")
        print(f"📋 问题: {question}")
        print("="*60)

        # 阶段1: 规划
        print("\n🔵 阶段1: 规划 (Plan-and-Solve)")
        plan = self._plan(question)
        if not plan:
            return "规划失败"

        # 阶段2: 执行 (ReAct)
        print(f"\n🟢 阶段2: 执行 (ReAct) - 共 {len(plan)} 个步骤")
        result, trajectory = self._execute(question, plan)

        # 阶段3: 反思
        print(f"\n🟡 阶段3: 反思 (Reflection)")
        feedback = self._reflect(question, trajectory, result)

        if "通过" in feedback:
            print(f"\n✅ 任务完成!")
            return result
        else:
            print(f"\n⚠️ 存在问题: {feedback}")
            print("（实际项目中可在此处进行迭代优化）")
            return result

    def _plan(self, question: str) -> List[str]:
        """规划阶段"""
        prompt = PLANNER_PROMPT.format(question=question)
        response = self.llm.think([{"role": "user", "content": prompt}])

        try:
            plan_str = response.split("```python")[1].split("```")[0].strip()
            import ast
            plan = ast.literal_eval(plan_str)
            print(f"📋 计划: {plan}")
            return plan
        except Exception as e:
            print(f"❌ 解析计划失败: {e}")
            return []

    def _execute(self, question: str, plan: List[str]) -> tuple:
        """执行阶段 - 使用 ReAct 模式"""
        history = ""
        trajectory = []
        tools_desc = "\n".join([f"- {k}: {v['desc']}" for k, v in TOOLS.items()])

        for i, step in enumerate(plan, 1):
            print(f"\n  📌 步骤 {i}/{len(plan)}: {step}")

            for attempt in range(self.max_steps):
                prompt = EXECUTOR_PROMPT.format(
                    question=question,
                    plan=plan,
                    history=history or "无",
                    current_step=step,
                    tools=tools_desc
                )

                response = self.llm.think([{"role": "user", "content": prompt}])

                # 解析 Action
                action_match = re.search(r"Action:\s*(.+)", response)
                if not action_match:
                    continue

                action = action_match.group(1).strip()

                # 检查 Finish
                if action.startswith("Finish"):
                    finish_match = re.search(r"Finish\[(.+)\]", action, re.DOTALL)
                    result = finish_match.group(1).strip() if finish_match else action
                    history += f"步骤{i}: {step}\n结果: {result}\n\n"
                    trajectory.append(f"步骤{i}: {step} → {result}")
                    print(f"  ✅ 结果: {result}")
                    break

                # 执行工具
                tool_match = re.match(r"(\w+)\[(.+)\]", action)
                if tool_match:
                    tool_name, tool_input = tool_match.groups()
                    if tool_name in TOOLS:
                        observation = TOOLS[tool_name]["func"](tool_input)
                        print(f"  🔧 工具: {tool_name} → {observation}")
                        history += f"Action: {action}\nObservation: {observation}\n"
                        trajectory.append(f"工具调用: {tool_name}[{tool_input}] → {observation}")

        return history.split("结果:")[-1].strip() if "结果:" in history else "执行完成", trajectory

    def _reflect(self, question: str, trajectory: list, result: str) -> str:
        """反思阶段"""
        prompt = REFLECTOR_PROMPT.format(
            question=question,
            trajectory="\n".join(trajectory),
            result=result
        )
        response = self.llm.think([{"role": "user", "content": prompt}])
        return response


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    llm = LLMClient()
    agent = HybridAgent(llm)

    # 测试问题
    question = "北京现在几点？天气怎么样？如果温度低于20度，告诉我应该穿什么衣服。"
    agent.run(question)
