# Day 5-7 学习笔记

> **日期**：2025-05-05
> **主题**：ReAct 范式深入 + 三种范式对比

---

## ✅ 完成情况

- [x] 阅读 ReAct 范式文档
- [x] 运行 Plan_and_solve.py 示例
- [x] 运行 Reflection.py 示例
- [x] 运行 ReAct_demo.py 示例
- [x] 深入理解三种范式代码实现
- [x] 三种范式对比分析
- [ ] 选择范式设计 Agent
- [ ] Week 1 总结

---

## 📝 学习内容

### 一、三种范式概述

| 范式 | 核心思想 | 适用场景 |
|------|----------|----------|
| **ReAct** | 思考-行动-观察循环 | 需要外部工具交互的任务 |
| **Plan-and-Solve** | 先规划后执行 | 结构性强、可分解的任务 |
| **Reflection** | 执行-反思-优化迭代 | 对结果质量要求高的任务 |

---

## 二、Plan-and-Solve 范式

### 核心流程

```
用户问题
    ↓
┌─────────────────────────────────────┐
│ 规划阶段 (Planner)                   │
│ 将问题分解为多个步骤                  │
│ 输出: ["步骤1", "步骤2", ...]        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 执行阶段 (Executor)                  │
│ 按顺序执行每个步骤                    │
│ 每步结果作为下一步的上下文            │
└─────────────────────────────────────┘
    ↓
最终答案
```

### 运行结果

**输入**：一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？

**规划阶段输出**：
```python
["确定周一卖出的苹果数量为15个", 
 "计算周二卖出的苹果数量：15个 × 2 = 30个", 
 "计算周三卖出的苹果数量：30个 - 5个 = 25个", 
 "计算三天总销量：15个 + 30个 + 25个 = 70个"]
```

**执行阶段**：
- 步骤 1: 15 ✅
- 步骤 2: 30 ✅
- 步骤 3: 25 ✅
- 步骤 4: 70 ✅

**最终答案**：70

### 关键代码分析

```python
class Planner:
    def plan(self, question: str) -> list[str]:
        # 使用提示词让 LLM 生成结构化计划
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        response = self.llm_client.think(messages=[...])
        # 解析 ```python [...] ``` 格式的输出
        plan = ast.literal_eval(plan_str)
        return plan

class Executor:
    def execute(self, question: str, plan: list[str]) -> str:
        history = ""
        for step in plan:
            # 每步都传入完整历史
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question, 
                plan=plan, 
                history=history, 
                current_step=step
            )
            result = self.llm_client.think(messages=[...])
            history += f"步骤: {step}\n结果: {result}\n\n"
        return result
```

**核心设计**：
- 使用 `ast.literal_eval` 安全解析 Python 列表字符串
- 执行器维护 `history` 状态，确保信息传递
- 提示词中包含完整计划和当前步骤，让模型专注执行

---

## 三、Reflection 范式

### 核心流程

```
用户任务
    ↓
┌─────────────────────────────────────┐
│ 初始执行 (Execution)                 │
│ 生成初版解决方案                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 反思循环 (直到无需改进或达到上限)     │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ 反思 (Reflection)               ││
│  │ 评审员分析问题，给出反馈         ││
│  └─────────────────────────────────┘│
│              ↓                      │
│  ┌─────────────────────────────────┐│
│  │ 优化 (Refinement)               ││
│  │ 根据反馈改进解决方案             ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
    ↓
最终优化方案
```

### 运行结果

**任务**：编写一个 Python 函数，找出 1 到 n 之间所有的素数。

**初始尝试**（埃拉托斯特尼筛法）：
```python
def find_primes_upto(n):
    # 时间复杂度 O(n log log n)
    sieve = [True] * (n + 1)
    ...
```

**第 1 轮反思**：
> 当前算法为标准埃拉托斯特尼筛法，时间复杂度 O(n log log n)。
> 建议改用欧拉筛（线性筛法），时间复杂度 O(n)。

**第 1 轮优化**：
```python
def find_primes_upto(n):
    # 欧拉筛法，时间复杂度 O(n)
    primes = []
    for i in range(2, n + 1):
        if sieve[i]:
            primes.append(i)
        for p in primes:
            ...
            if i % p == 0:  # 关键优化
                break
    return primes
```

**第 2 轮反思**：
> 无需改进。算法已达到理论最优时间复杂度 O(n)。

**最终代码**：欧拉筛法实现 ✅

### 关键代码分析

```python
class Memory:
    """记忆模块 - 存储执行和反思轨迹"""
    def add_record(self, record_type: str, content: str):
        self.records.append({"type": record_type, "content": content})
    
    def get_trajectory(self) -> str:
        # 格式化历史记录供提示词使用
        ...

class ReflectionAgent:
    def run(self, task: str):
        # 1. 初始执行
        initial_code = self._get_llm_response(INITIAL_PROMPT)
        self.memory.add_record("execution", initial_code)
        
        # 2. 迭代循环
        for i in range(self.max_iterations):
            # 反思
            feedback = self._get_llm_response(REFLECT_PROMPT)
            if "无需改进" in feedback:
                break
            # 优化
            refined_code = self._get_llm_response(REFINE_PROMPT)
            self.memory.add_record("execution", refined_code)
```

**核心设计**：
- 记忆模块存储完整轨迹，提供上下文
- 三套提示词：执行、反思、优化，各司其职
- 终止条件：反馈包含"无需改进"或达到最大迭代次数

---

## 四、ReAct 范式

### 核心流程

```
用户问题
    ↓
┌─────────────────────────────────────┐
│ Thought: 分析问题，决定下一步        │
│ Action: 调用工具或输出答案           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Observation: 工具返回结果            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 继续循环或 Finish[最终答案]          │
└─────────────────────────────────────┘
```

### 运行结果

**输入**：北京今天天气怎么样？

**执行过程**：
```
第 1 步：
  Thought: 用户询问北京的天气，需要调用天气查询工具。
  Action: get_weather[北京]
  Observation: 北京当前天气：Sunny，气温29摄氏度

第 2 步：
  Thought: 已获取北京天气信息，可以生成回答。
  Action: Finish[北京今天晴，气温在20到25摄氏度之间。]
```

### 关键代码分析

```python
class ReActAgent:
    def run(self, question: str):
        while current_step < self.max_steps:
            # 1. 构建提示词（包含工具描述和历史）
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc, 
                question=question, 
                history=history_str
            )
            
            # 2. LLM 思考
            response = self.llm_client.think(messages=[...])
            
            # 3. 解析 Thought 和 Action
            thought, action = self._parse_output(response)
            
            # 4. 执行 Action
            if action.startswith("Finish"):
                return self._parse_action_input(action)
            
            # 5. 调用工具
            tool_function = self.tool_executor.getTool(tool_name)
            observation = tool_function(tool_input)
            
            # 6. 记录历史
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")
```

---

## 五、三种范式对比分析

### 1. 工作方式对比

| 维度 | ReAct | Plan-and-Solve | Reflection |
|------|-------|----------------|------------|
| **决策模式** | 动态反应式 | 预先规划式 | 迭代优化式 |
| **执行顺序** | 边想边做 | 先规划后执行 | 边做边改 |
| **历史处理** | 追加 Observation | 累积步骤结果 | 存储完整轨迹 |
| **终止条件** | Finish 或超时 | 计划执行完毕 | 无需改进或超限 |

### 2. 适用场景对比

```
任务特征                推荐范式
─────────────────────────────────
需要外部工具交互    →    ReAct
结构性强、可分解    →    Plan-and-Solve
对结果质量要求高    →    Reflection
需要实时信息查询    →    ReAct
多步推理问题        →    Plan-and-Solve
代码生成与优化      →    Reflection
```

### 3. 优缺点对比

#### ReAct
- ✅ 高可解释性（Thought 链清晰）
- ✅ 动态纠错能力
- ❌ 依赖 LLM 格式遵循能力
- ❌ 可能陷入循环

#### Plan-and-Solve
- ✅ 结构清晰，步骤明确
- ✅ 适合复杂推理任务
- ❌ 计划静态，无法动态调整
- ❌ 如果计划错误，执行也会失败

#### Reflection
- ✅ 显著提升输出质量
- ✅ 内部纠错能力
- ❌ 调用成本高（多次迭代）
- ❌ 实时性差

### 4. 组合使用思路

可以组合使用三种范式：

```
┌─────────────────────────────────────────────────────────┐
│                    混合范式架构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Plan-and-Solve: 先生成整体计划                       │
│           ↓                                             │
│  2. ReAct: 执行每个步骤（可调用工具）                     │
│           ↓                                             │
│  3. Reflection: 对关键结果进行反思优化                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 六、代码架构对比

### 共同点
1. 都有 LLM 客户端封装
2. 都使用提示词模板
3. 都有输出解析逻辑

### 差异点

| 组件 | ReAct | Plan-and-Solve | Reflection |
|------|-------|----------------|------------|
| **核心类** | ReActAgent | Planner + Executor + Agent | Memory + Agent |
| **提示词数量** | 1 | 2（规划+执行） | 3（执行+反思+优化） |
| **状态管理** | history 列表 | history 字符串 | Memory 类 |
| **解析复杂度** | 中等 | 高（解析 Python 列表） | 低 |

---

## 💡 心得体会

### 最有收获的内容

1. **范式选择的本质**：不同的范式解决不同类型的问题，没有万能方案
2. **提示词设计的重要性**：精确的格式说明是 Agent 稳定运行的基础
3. **迭代优化的价值**：Reflection 范式展示了如何通过自我批评提升质量

### 学习方法总结

**有效的做法**：
- 先阅读文档理解理论，再运行代码验证
- 对比三种范式的代码结构，理解设计差异
- 记录运行结果，方便后续回顾

---

## 📌 待解决问题

- [ ] 设计一个组合范式的 Agent
- [ ] 配置 Tavily API 测试搜索功能
- [ ] 完成 Week 1 总结

---

## 📊 今日统计

| 统计项 | 数值 |
|--------|------|
| 投入时间 | 约 2 小时 |
| 完成任务 | 6 / 8 |
| 运行代码次数 | 3 |
| 发现问题 | 0 |

---

*完成时间：2025-05-05*
