"""
ReAct 范式演示 - 简化版

使用天气和计算工具演示 ReAct 循环
"""

import re
import requests
from llm_client import HelloAgentsLLM
from typing import Dict, Any

# ============================================================================
# 1. 定义工具函数
# ============================================================================

def get_weather(city: str) -> str:
    """查询城市天气"""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data['current_condition'][0]
        weather_desc = current['weatherDesc'][0]['value']
        temp_c = current['temp_C']

        return f"{city}当前天气：{weather_desc}，气温{temp_c}摄氏度"

    except Exception as e:
        return f"查询天气失败：{e}"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        allowed = set('0123456789+-*/(). ')
        if not all(c in allowed for c in expression):
            return "错误：只支持基本数学运算"

        result = eval(expression)
        return f"计算结果：{expression} = {result}"

    except Exception as e:
        return f"计算错误：{e}"


def get_time(city: str) -> str:
    """查询城市当前时间（本地计算，无需API）"""
    from datetime import datetime
    import pytz

    # 城市时区映射
    timezone_map = {
        "北京": "Asia/Shanghai",
        "上海": "Asia/Shanghai",
        "东京": "Asia/Tokyo",
        "纽约": "America/New_York",
        "伦敦": "Europe/London",
        "巴黎": "Europe/Paris",
        "悉尼": "Australia/Sydney",
    }

    # 默认使用中国时区
    tz_name = timezone_map.get(city, "Asia/Shanghai")

    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        return f"{city}当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"
    except Exception as e:
        return f"查询时间失败：{e}"


# ============================================================================
# 2. 工具执行器
# ============================================================================

class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")

        self.tools[name] = {"description": description, "func": func}
        print(f"✅ 工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])


# ============================================================================
# 3. ReAct 提示词模板
# ============================================================================

REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回应：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一：
- `{{tool_name}}[{{tool_input}}]`：调用一个可用工具。
- `Finish[最终答案]`：当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `Finish[最终答案]` 来输出最终答案。


现在，请开始解决以下问题：
Question: {question}
History: {history}
"""


# ============================================================================
# 4. ReAct 智能体
# ============================================================================

class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        self.history = []
        current_step = 0

        print(f"\n{'='*60}")
        print(f"📋 用户问题: {question}")
        print("="*60)

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n{'─'*60}")
            print(f"🔄 第 {current_step} 步")
            print("─"*60)

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(tools=tools_desc, question=question, history=history_str)

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            if not response_text:
                print("错误：LLM未能返回有效响应。")
                break

            thought, action = self._parse_output(response_text)
            if thought:
                print(f"\n💭 思考: {thought}")
            if not action:
                print("警告：未能解析出有效的Action，流程终止。")
                break

            if action.startswith("Finish"):
                # 如果是Finish指令，提取最终答案并结束
                final_answer = self._parse_action_input(action)
                print(f"\n🎉 最终答案: {final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                self.history.append("Observation: 无效的Action格式，请检查。")
                continue

            print(f"\n🎬 行动: {tool_name}[{tool_input}]")
            tool_function = self.tool_executor.getTool(tool_name)
            observation = tool_function(tool_input) if tool_function else f"错误：未找到名为 '{tool_name}' 的工具。"

            print(f"\n👀 观察: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("\n已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        return (match.group(1), match.group(2)) if match else (None, None)

    def _parse_action_input(self, action_text: str):
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        return match.group(1) if match else ""


# ============================================================================
# 5. 主程序
# ============================================================================

if __name__ == '__main__':
    # 初始化 LLM 客户端
    llm = HelloAgentsLLM()

    # 初始化工具执行器
    tool_executor = ToolExecutor()

    # 注册工具
    weather_desc = "查询指定城市的实时天气。参数：城市名称（如：北京、上海）"
    calc_desc = "计算数学表达式。参数：数学表达式（如：123*456、(100+200)/3）"
    time_desc = "查询指定城市的当前时间。参数：城市名称（如：北京、东京、纽约）"

    tool_executor.registerTool("get_weather", weather_desc, get_weather)
    tool_executor.registerTool("calculate", calc_desc, calculate)
    tool_executor.registerTool("get_time", time_desc, get_time)  # 新增：时间查询工具

    # 创建智能体
    agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)

    # 测试问题
    questions = [
        "北京现在几点了？",
        # "帮我算一下 123 * 456",
        # "上海天气如何？如果温度低于20度，建议穿什么？"
    ]

    for question in questions:
        agent.run(question)
        print("\n")
