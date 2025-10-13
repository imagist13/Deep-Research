"""
规划器提示词定义
用于生成研究计划
"""

MASTER_PLANNER_PROMPT = """
你是一位专业的研究规划师。你的任务是根据用户的查询，制定一个详细的研究和写作计划。

用户查询: {query}

请按照以下JSON格式输出你的计划：

{{
  "overall_outline": "整个报告的总大纲和结构说明",
  "plan": [
    {{
      "item_id": "research_1",
      "task_type": "RESEARCH",
      "description": "研究任务的具体描述",
      "dependencies": []
    }},
    {{
      "item_id": "research_2", 
      "task_type": "RESEARCH",
      "description": "另一个研究任务",
      "dependencies": []
    }},
    {{
      "item_id": "writing_1",
      "task_type": "WRITING", 
      "description": "基于研究结果写作的章节",
      "dependencies": ["research_1", "research_2"]
    }}
  ]
}}

重要规则：
1. 先安排所有RESEARCH任务，再安排WRITING任务
2. WRITING任务的dependencies必须包含相关的RESEARCH任务ID
3. 每个任务都要有唯一的item_id
4. 确保计划逻辑清晰，依赖关系正确
5. 总大纲要简洁明了，概括整个报告的结构

请直接返回JSON，不要包含其他解释文字。
"""
