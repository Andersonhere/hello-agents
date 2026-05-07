"""
Day 9 手写极简版 SimpleAgent —— 骨架提示卡

【规则】
1. 不看 HelloAgents 源码，自己写
2. 总行数 ≤ 50（不含注释和空行）
3. 必须能跑通 main() 里的测试
4. 跑通后再对比官方 SimpleAgent 源码

【核心问题（写之前先回答）】
- 一个 SimpleAgent 至少需要哪几个属性？（提示：3 个）
- run(user_input) 的执行流程是什么？（提示：4 步）
- 对话历史 messages 应该长什么样？（提示：OpenAI 格式）

【依赖】
- 你已经有 LLM key 和可用的 client（参考你 Week 1 的 first_agent.py）
- 不要引入除 LLM client 之外的任何依赖

==============================================================
                     ↓ 在下面动手写 ↓
==============================================================
"""

# TODO 1: 导入你的 LLM client（复用 Week 1 的方式）
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv() 

# TODO 2: 定义 MiniSimpleAgent 类
class MiniSimpleAgent:
    """极简版 SimpleAgent，目标 ≤ 50 行"""

    def __init__(self, system_prompt: str = "你是一个有帮助的助手。"):
        # TODO: 初始化 3 样东西
        # - self.llm: LLM 客户端
        self.llm = OpenAI(api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),)
        # - self.system_prompt: 系统提示词
        self.system_prompt = system_prompt
        # - self.messages: 对话历史（list），首条是 system role
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.model = os.getenv("LLM_MODEL_ID", "Qwen3-235B-A22B")  # 第二个参数是默认值

    def run(self, user_input: str) -> str:
        """
        TODO: 实现 4 步流程
        Step 1: 把 user_input 追加到 self.messages
        
        Step 2: 调 self.llm 拿到回复
        Step 3: 把回复追加到 self.messages（保持多轮上下文）
        Step 4: 返回回复内容
        """
        
        self.messages.append({"role": "user", "content": user_input})
        
        response = self.llm.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0
        )
        
        # 提取回复内容
        content = response.choices[0].message.content
        
        # 追加到对话历史
        self.messages.append({"role": "assistant", "content": content})
        
        return content

    def reset(self):
        """TODO: 清空对话历史，但保留 system_prompt"""
        self.messages = [{"role": "system", "content": self.system_prompt}]


# ==============================================================
#                    自测：跑通下面才算 Day 9 完成
# ==============================================================
def main():
    agent = MiniSimpleAgent(system_prompt="你是一个简洁的中文助手，回答不超过 30 字。")

    # 测试 1：基础问答
    print("Q1:", agent.run("你好，你是谁？"))

    # 测试 2：多轮上下文（关键！如果没记住，说明 messages 没正确累积）
    print("Q2:", agent.run("我刚才问了你什么？"))

    # 测试 3：reset 后应该忘记上文
    agent.reset()
    print("Q3 (after reset):", agent.run("我刚才问了你什么？"))


if __name__ == "__main__":
    main()


# ==============================================================
#                  完成后回答这 3 个问题（写到笔记里）
# ==============================================================
# Q1. 你的实现里"对话历史"是怎么管理的？如果 messages 越来越长会怎样？
# A1. 对话历史通过self.messages列表管理，每次对话都会将用户输入和助手回复添加到列表中，如果messages越来越长，会导致对话历史过长，影响模型的响应速度和准确性。
# Q2. 如果用户问"调用 xxx 工具"，你这个版本能做到吗？为什么？
# A2. 这个版本做不到，因为没有定义工具说明，没有给大模型传递工具描述
#     （这就是 Day 10 ReAct 要解决的问题）
# Q3. 对比官方 SimpleAgent 源码，你少了哪些功能？哪些是"工程必要"哪些是"锦上添花"？
# A3. 对比官方 SimpleAgent，我的版本缺失：
#
# 【工程必要 —— 没有会出 bug 或不可用】
# 1. 工具调用循环 + 迭代上限 (max_tool_iterations=3)
#    原因：没有循环工具调用不了；没有上限 LLM 可能无限反复调用同一工具
# 2. 错误处理与重试 (LLM 调用层)
#    原因：网络超时/限流/返回 None 都会炸掉整个对话
# 3. 对话历史用 Message 对象而非 dict
#    原因：对象可扩展字段（timestamp、metadata），dict 一旦落库就难改
# 4. 基类继承 (SimpleAgent -> BaseAgent)
#    原因：统一的 add_message/get_history 接口，否则每个 Agent 自己实现一套
#
# 【锦上添花 —— 没有也能跑，但产品体验差】
# 1. 流式输出 (run_stream + Iterator)
#    原因：等 10 秒一次性吐出 vs 1 秒后开始逐字显示，UX 差距巨大
# 2. system_prompt 运行时动态生成 (_get_enhanced_system_prompt)
#    原因：工具列表可以动态变，每次 run 重新拼 prompt 比写死灵活
# 3. 工具运行时增删 (add_tool/remove_tool/list_tools)
#    原因：同一个 Agent 不同场景下可以挂载不同工具集