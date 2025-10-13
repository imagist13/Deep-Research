"""
Deep Search Agent 启动脚本
提供交互式命令行界面
"""

import asyncio
import os
import sys
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from angent import DeepSearchAgent
from config.logging_config import get_logger

logger = get_logger(__name__)


class DeepSearchCLI:
    """Deep Search 命令行界面"""
    
    def __init__(self):
        self.agent = None
        self.chat_history = []
    
    async def initialize(self):
        """初始化智能体"""
        try:
            print("正在初始化Deep Search Agent...")
            self.agent = DeepSearchAgent()
            print("✅ 初始化完成！")
            return True
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """处理用户查询"""
        if not self.agent:
            return {"success": False, "error": "智能体未初始化"}
        
        try:
            print(f"\n🔍 正在处理查询: {query}")
            print("⏳ 请稍候，这可能需要几分钟...")
            
            result = await self.agent.search_and_generate_report(
                query=query,
                chat_history=self.chat_history
            )
            
            # 更新对话历史
            self.chat_history.append({"role": "user", "content": query})
            if result["success"]:
                self.chat_history.append({"role": "assistant", "content": result["report"]})
            
            return result
        except Exception as e:
            logger.error(f"处理查询时发生错误: {e}")
            return {"success": False, "error": str(e)}
    
    def display_result(self, result: Dict[str, Any]):
        """显示结果"""
        if not result["success"]:
            print(f"\n❌ 处理失败: {result['error']}")
            return
        
        print("\n" + "=" * 60)
        print("📄 生成的报告")
        print("=" * 60)
        
        if result.get("outline"):
            print(f"\n📋 报告大纲:\n{result['outline']}\n")
        
        if result.get("report"):
            print(f"\n📝 报告内容:\n{result['report']}\n")
        
        if result.get("sources"):
            print(f"\n📚 参考文献 ({len(result['sources'])} 个):")
            print("-" * 40)
            for source in result["sources"]:
                print(f"[{source['number']}] {source['title']}")
                print(f"    {source['url']}")
        
        if result.get("errors"):
            print(f"\n⚠️  警告信息:")
            for error in result["errors"]:
                print(f"  - {error}")
    
    async def interactive_mode(self):
        """交互模式"""
        print("\n🎯 Deep Search Agent 交互模式")
        print("输入 'quit' 或 'exit' 退出")
        print("输入 'status' 查看状态")
        print("输入 'clear' 清空对话历史")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n💬 请输入您的研究问题: ").strip()
                
                if query.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break
                
                if query.lower() == 'status':
                    if self.agent:
                        status = self.agent.get_status()
                        print(f"\n📊 系统状态: {status['status']}")
                        print(f"🤖 模型: {status['model_info']['model']}")
                        print(f"🔧 功能: {', '.join(status['features'])}")
                    else:
                        print("❌ 智能体未初始化")
                    continue
                
                if query.lower() == 'clear':
                    self.chat_history = []
                    print("✅ 对话历史已清空")
                    continue
                
                if not query:
                    print("⚠️  请输入有效的问题")
                    continue
                
                # 处理查询
                result = await self.process_query(query)
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
    
    async def run(self):
        """运行CLI"""
        print("🚀 Deep Search Agent")
        print("=" * 50)
        
        # 检查环境变量
        if not os.getenv("DEEPSEEK_API_KEY"):
            print("❌ 错误: 未设置DEEPSEEK_API_KEY环境变量")
            print("请创建.env文件并设置API密钥")
            return
        
        # 初始化
        if not await self.initialize():
            return
        
        # 进入交互模式
        await self.interactive_mode()


async def main():
    """主函数"""
    cli = DeepSearchCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
