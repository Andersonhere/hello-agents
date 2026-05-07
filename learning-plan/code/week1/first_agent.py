"""
第一个 Agent 测试代码

学习目标：
1. 理解 Agent 基本工作流程
2. 理解 ReAct 模式（思考-行动-观察）
3. 学会使用工具扩展 Agent 能力
"""

import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()


# ============================================================================
# 1. 定义工具函数
# ============================================================================

def get_weather(city: str) -> str:
    """查询城市天气"""
    import requests

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


# 可用工具字典
TOOLS = {
    "get_weather": {
        "func": get_weather,
        "description": "查询指定城市的天气。参数：city（城市名称）"
    },
    "calculate": {
        "func": calculate,
        "description": "计算数学表达式。参数：expression（数学表达式）"
    }
}


# ============================================================================
# 2. Agent 系统提示词
# ============================================================================

AGENT_PROMPT = """你是一个智能助手，可以使用工具帮助用户解决问题。

# 可用工具
{tools}

# 输出格式
每次回复必须包含 Thought 和 Action（每行一个）：

Thought: [你的思考过程]
Action: [工具名(参数)] 或 Finish[最终答案]

# 示例
用户：北京天气怎么样？
Thought: 用户想知道北京天气，我需要调用天气查询工具
Action: get_weather(city="北京")

用户：123+456等于多少？
Thought: 这是一个数学计算问题
Action: calculate(expression="123+456")

# 重要规则
1. 每次只输出一个 Thought 和一个 Action
2. Action 后面不要有多余内容
3. 获得工具结果后，用 Finish 输出最终答案
4. Finish 格式：Finish[你的最终答案]
"""


# ============================================================================
# 3. Agent 类
# ============================================================================

class SimpleAgent:
    """简单的 ReAct Agent"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        self.model = os.getenv("LLM_MODEL_ID")
        self.history = []

    def run(self, question: str, max_steps: int = 5) -> str:
        """运行 Agent"""
        self.history = []

        # 构建提示词
        tools_desc = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in TOOLS.items()
        ])
        prompt = AGENT_PROMPT.format(tools=tools_desc)

        print(f"\n{'='*60}")
        print("📄 完整系统提示词:")
        print("=" * 60)
        print(prompt)
        print("=" * 60)

        print(f"\n❓ 用户问题: {question}")
        print("=" * 60)

        for step in range(max_steps):
            print(f"\n{'─'*60}")
            print(f"🔄 第 {step + 1} 步")
            print("─" * 60)

            # 构建消息
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ]

            # 添加历史观察
            if self.history:
                print(f"\n📚 历史记录 ({len(self.history)} 条):")
                for i, h in enumerate(self.history, 1):
                    print(f"   {i}. {h[:80]}...")

                for h in self.history:
                    messages.append({"role": "user", "content": h})

            print(f"\n📨 发送给 LLM 的消息:")
            print("-" * 40)
            for i, msg in enumerate(messages, 1):
                role = msg["role"]
                content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                print(f"   [{i}] {role}: {content}")
            print("-" * 40)

            # 调用 LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0
            )

            output = response.choices[0].message.content
            print(f"\n🤖 模型原始输出:")
            print("-" * 40)
            print(output)
            print("-" * 40)

            # 解析 Thought
            thought_match = re.search(r'Thought:\s*(.+?)(?=\n|$)', output, re.DOTALL)
            if thought_match:
                print(f"💭 Thought: {thought_match.group(1).strip()}")

            # 解析 Action
            action_match = re.search(r'Action:\s*(.+)', output)

            # 检查是否有直接的 Finish（没有 Action: 前缀）
            direct_finish = re.search(r'Finish\[(.+)\]', output, re.DOTALL)

            if direct_finish:
                print(f"🏁 检测到 Finish（无 Action 前缀）")
                return direct_finish.group(1).strip()

            if not action_match:
                print("⚠️ 未找到 Action，继续下一轮...")
                continue

            action = action_match.group(1).strip()
            print(f"🎬 Action: {action}")

            # 检查是否结束
            if action.startswith("Finish"):
                final = re.search(r'Finish\[(.+)\]', action, re.DOTALL)
                print(f"🏁 检测到 Finish（有 Action 前缀）")
                if final:
                    return final.group(1).strip()
                else:
                    return action.replace("Finish", "").strip("[] ")

            # 解析工具调用
            tool_match = re.match(r'(\w+)\((.+)\)', action)
            if not tool_match:
                self.history.append(f"Observation: 无法解析工具调用")
                print(f"⚠️ 无法解析工具调用")
                continue

            tool_name = tool_match.group(1)
            params_str = tool_match.group(2)
            print(f"📦 工具名: {tool_name}")
            print(f"📋 参数字符串: {params_str}")

            # 解析参数
            params = {}
            for match in re.finditer(r'(\w+)=["\'](.+?)["\']', params_str):
                params[match.group(1)] = match.group(2)

            # 如果没有命名参数，尝试位置参数
            if not params and params_str:
                params = {"input": params_str.strip('"\'')}

            print(f"🔧 解析后参数: {params}")

            # 执行工具
            if tool_name in TOOLS:
                print(f"🚀 执行工具: {tool_name}...")
                result = TOOLS[tool_name]["func"](**params)
                print(f"📥 工具返回: {result}")
                self.history.append(f"Observation: {result}")

                # 检查结果中是否已经包含最终答案
                if "Finish" in output:
                    finish_match = re.search(r'Finish\[(.+)\]', output)
                    if finish_match:
                        return finish_match.group(1).strip()
            else:
                print(f"❌ 未知工具: {tool_name}")
                self.history.append(f"Observation: 未知工具 {tool_name}")

        return "达到最大步数限制"


# ============================================================================
# 4. 主程序
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("第一个 Agent 测试")
    print("=" * 60)

    # 检查环境变量
    if not os.getenv("LLM_API_KEY"):
        print("错误：请先配置 .env 文件")
        exit(1)

    agent = SimpleAgent()

    # 预设测试用例（只运行一个，方便查看完整输出）
    test_cases = [
        "北京今天天气怎么样？",
        # "帮我算一下 123 * 456",
        # "上海天气如何？温度是多少？",
    ]

    for i, question in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {question}")
        print("=" * 60)

        answer = agent.run(question)
        print(f"\n💬 最终答案: {answer}")
