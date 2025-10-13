"""
Deep Search Agent 主入口文件
提供完整的深度搜索和报告生成功能
"""

import asyncio
import os
from typing import Dict, Any, Optional
from config.logging_config import get_logger
from config.settings import settings
from graphs.deepsearch_graph import DeepSearchGraph
from schemas.graph_state import AgentState

logger = get_logger(__name__)


class DeepSearchAgent:
    """深度搜索智能体主类"""
    
    def __init__(self):
        """初始化智能体"""
        self.graph = DeepSearchGraph()
        self.app = self.graph.get_app()
        logger.info("DeepSearchAgent 初始化完成")
    
    async def search_and_generate_report(
        self, 
        query: str, 
        chat_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        执行深度搜索并生成报告
        
        Args:
            query: 用户查询
            chat_history: 对话历史
            
        Returns:
            包含报告和来源的字典
        """
        try:
            logger.info(f"开始处理查询: {query}")
            
            # 构建初始状态
            initial_state: AgentState = {
                "input": query,
                "chat_history": chat_history or [],
                "overall_outline": None,
                "plan": [],
                "final_answer": "",
                "final_sources": [],
                "current_plan_item_id": None,
                "supervisor_decision": "",
                "step_count": 0,
                "error_log": [],
                "shared_context": {
                    "citations": {},
                    "next_citation_number": 1
                },
                "next_step_index": 0
            }
            
            # 执行工作流
            result = await self.app.ainvoke(initial_state)
            
            logger.info("深度搜索和报告生成完成")
            return {
                "success": True,
                "report": result.get("final_answer", ""),
                "sources": result.get("final_sources", []),
                "outline": result.get("overall_outline", ""),
                "plan": result.get("plan", []),
                "errors": result.get("error_log", [])
            }
            
        except Exception as e:
            logger.error(f"处理查询时发生错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "report": "",
                "sources": [],
                "outline": "",
                "plan": [],
                "errors": [{"node": "main", "error": str(e)}]
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态信息"""
        return {
            "status": "ready",
            "model_info": {
                "provider": "DeepSeek",
                "model": settings.DEEPSEEK_CHAT_MODEL,
                "api_base": settings.DEEPSEEK_BASE_URL
            },
            "features": [
                "深度网络搜索",
                "智能研究规划", 
                "自动报告生成",
                "引用管理",
                "向量知识库"
            ]
        }


async def main():
    """主函数，用于测试"""
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("错误: 请设置DEEPSEEK_API_KEY环境变量")
        return
    
    if not os.getenv("DASH_SCOPE_API_KEY"):
        print("警告: 未设置DASH_SCOPE_API_KEY，嵌入功能可能受限")
    
    # 创建智能体
    agent = DeepSearchAgent()
    
    # 测试查询
    test_query = "人工智能在医疗领域的应用现状和发展趋势"
    
    print(f"开始处理查询: {test_query}")
    print("=" * 50)
    
    result = await agent.search_and_generate_report(test_query)
    
    if result["success"]:
        print("报告生成成功!")
        print(f"大纲: {result['outline']}")
        print(f"报告长度: {len(result['report'])} 字符")
        print(f"引用数量: {len(result['sources'])}")
        print("\n报告内容:")
        print("-" * 30)
        print(result['report'])
        
        if result['sources']:
            print("\n参考文献:")
            print("-" * 30)
            for source in result['sources']:
                print(f"[{source['number']}] {source['title']}")
                print(f"    {source['url']}")
    else:
        print(f"报告生成失败: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
