import os
import json
import requests
from dotenv import load_dotenv
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 加载环境变量
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

# 阿里云通义千问接口地址
url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 任务拆解器
def task_decomposer(complex_task):
    prompt = f"""请将以下复杂任务拆解为7-10个具体、可执行的子任务，
    每个子任务包含"description"（任务描述）和"tool"（所需工具）字段，
    直接以JSON数组格式返回，不要添加任何多余内容，也不要加任何解释文字：
    复杂任务：{complex_task}
    示例：[{{"description": "查询三亚下周天气", "tool": "天气API"}}]"""

    data = {
        "model": "qwen-turbo",
        "input": {
            "messages": [{"role": "user", "content": prompt}]
        },
        "parameters": {
            "temperature": 0.3
        }
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    content = result["output"]["text"].strip()
    
    # 兼容不同格式，直接返回解析后的列表
    json_result = json.loads(content)
    if isinstance(json_result, dict) and "subtasks" in json_result:
        return json_result["subtasks"]
    else:
        return json_result  # 直接返回数组

# 简单 Agent
def simple_agent(complex_task):
    print("接收到复杂任务：", complex_task)
    print("Agent正在拆解任务...")

    subtasks = task_decomposer(complex_task)

    print("拆解完成，共", len(subtasks), "个子任务：")
    for i, subtask in enumerate(subtasks, 1):
        print(f"  {i}. 任务：{subtask['description']} | 所需工具：{subtask['tool']}")

# 测试
if __name__ == "__main__":
    user_task = "帮我规划一份五天两人马尔代夫短途游，预算70000元，主打休闲娱乐，不要太累"
    simple_agent(user_task)