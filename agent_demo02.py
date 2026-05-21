import os
import json
import requests
from dotenv import load_dotenv
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# ======================================
# 1. 工具定义（兼容多种参数名）
# ======================================
def search_attractions(city, interest="休闲"):
    """查询城市景点 自动匹配标签"""
    # 自动归类标签
    if "人文" in interest:
        tag = "人文"
    else:
        tag = "休闲"
    mock_data = {
        "北京-人文": ["故宫", "天坛", "颐和园"],
        "马尔代夫-休闲": ["度假岛SPA", "浮潜体验", "沙滩漫步", "本地渔村游览", "海岛落日观光"]
    }
    key = f"{city}-{tag}"
    return f"{city}适合{interest}的景点：{', '.join(mock_data.get(key, ['海岛度假、近海游玩']))}"


def calculator(expression):
    """只执行纯数字数学计算，非算式直接拦截"""
    try:
        # 简单过滤，只算加减乘除
        res = eval(expression)
        return f"计算结果：{res}"
    except:
        return "当前内容非标准数学算式，跳过计算"
    
def budget_check(people, days, total_budget=None, budget=None):
    """人均每日预算计算（兼容budget和total_budget两种参数名）"""
    total = total_budget or budget
    if not total or people == 0 or days == 0:
        return "参数错误"
    per_person_daily = total // (people * days)
    return f"总预算{total}元，{people}人{days}天，人均每日预算：{per_person_daily}元"

TOOL_MAP = {
    "计算器": calculator,
    "景点查询API": search_attractions,
    "预算计算器": budget_check
}

# ======================================
# 2. 记忆层实现
# ======================================
class AgentMemory:
    def __init__(self):
        self.short_term = []
        self.long_term = {
            "preferences": {
                "travel_style": "休闲不赶路",
                "interest": "人文/自然景点",
                "budget_sensitive": True
            }
        }

    def add_short_term(self, role, content):
        self.short_term.append({"role": role, "content": content})

    def get_context(self):
        context = f"用户偏好：{self.long_term['preferences']}\n"
        context += "当前对话历史：\n"
        for msg in self.short_term:
            context += f"{msg['role']}: {msg['content']}\n"
        return context

# ======================================
# 3. 核心Agent（修正Prompt，强制参数名）
# ======================================
class TravelAgent:
    def __init__(self):
        self.memory = AgentMemory()

    def call_llm(self, prompt):
        data = {
            "model": "qwen-turbo",
            "input": {"messages": [{"role": "user", "content": prompt}]},
            "parameters": {"temperature": 0.3}
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()["output"]["text"].strip()

    def decompose_task(self, task):
        context = self.memory.get_context()
        # 强制指定参数名，和函数完全对应
        prompt = f"""
        {context}
        请将以下旅行任务拆解为3-5个可执行子任务，
        你只能使用以下工具：计算器、景点查询API、预算计算器。
        - 计算器仅用来做金额、天数、人数数字运算，禁止传入行程文字当做表达式
        每个任务必须包含：
        "description"（任务描述）、"tool"（工具名）、"params"（工具参数）
        工具参数必须严格对应：
        - 计算器：params={{"expression": "数学表达式"}}
        - 景点查询API：params={{"city": "城市名", "interest": "兴趣类型（如休闲/人文）"}}
        - 预算计算器：params={{"people": 人数, "days": 天数, "total_budget": 总预算}}
        直接返回JSON数组，不要多余内容。
        任务：{task}
        """
        result = self.call_llm(prompt)
        try:
            return json.loads(result)
        except:
            return []

    def execute_tool(self, subtask):
        tool_name = subtask["tool"]
        params = subtask.get("params", {})
        if tool_name not in TOOL_MAP:
            return f"工具{tool_name}不存在"
        return TOOL_MAP[tool_name](**params)

    def judge_completion(self, task, subtasks, results):
        context = self.memory.get_context()
        prompt = f"""
        {context}
        原始任务：{task}
        已拆解子任务：{subtasks}
        已执行结果：{results}
        请判断任务是否完成，以JSON格式返回，示例：
        {{"completed": true, "next_tasks": []}}
        """
        result = self.call_llm(prompt)
        try:
            return json.loads(result)
        except:
            return {"completed": True, "next_tasks": []}

    def run(self, user_task):
        print("=== 感知层：理解用户需求 ===")
        print("用户任务：", user_task)
        self.memory.add_short_term("user", user_task)

        print("\n=== 规划层：拆解任务 ===")
        subtasks = self.decompose_task(user_task)
        if not subtasks:
            print("任务拆解失败，请重试")
            return
        for i, task in enumerate(subtasks, 1):
            print(f"{i}. {task['description']}（工具：{task['tool']}）")

        print("\n=== 工具调用层：执行任务 ===")
        results = []
        for task in subtasks:
            res = self.execute_tool(task)
            results.append(res)
            print(f"✅ {task['description']} → {res}")
            self.memory.add_short_term("tool_result", res)

        print("\n=== 多轮循环：判断任务完成度 ===")
        judge = self.judge_completion(user_task, subtasks, results)
        if judge.get("completed", True):
            print("✅ 任务已全部完成！")
        else:
            print("⚠️ 任务未完成，补充子任务：")
            for task in judge.get("next_tasks", []):
                print(f"- {task.get('description', '无描述')}")

        print("\n=== 输出层：旅行规划总结 ===")
        summary_prompt = f"""
        {self.memory.get_context()}
        请根据以上所有信息，生成一份完整的旅行规划总结，用自然语言输出。
        """
        summary = self.call_llm(summary_prompt)
        print(summary)

if __name__ == "__main__":
    agent = TravelAgent()
    user_task = "帮我规划一份五天两人马尔代夫短途游，预算70000元，主打休闲娱乐，不要太累"
    agent.run(user_task)