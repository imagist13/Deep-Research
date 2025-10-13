"""
Deep Search Agent 测试脚本
用于验证各个组件的功能
"""

import asyncio
import os
import sys
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


async def test_config():
    """测试配置加载"""
    print("=== 测试配置加载 ===")
    try:
        print(f"应用名称: {settings.APP_NAME}")
        print(f"DeepSeek模型: {settings.DEEPSEEK_CHAT_MODEL}")
        print(f"DeepSeek API URL: {settings.DEEPSEEK_BASE_URL}")
        print("✅ 配置加载成功")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


async def test_llm():
    """测试LLM连接"""
    print("\n=== 测试LLM连接 ===")
    try:
        from llms.openai_llm import get_chat_model
        llm = get_chat_model()
        
        # 简单测试
        response = await llm.ainvoke("你好，请简单回复'测试成功'")
        print(f"LLM响应: {response.content}")
        print("✅ LLM连接成功")
        return True
    except Exception as e:
        print(f"❌ LLM连接失败: {e}")
        return False


async def test_search():
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")
    try:
        from tools.search_tools import search_tool
        
        # 执行搜索
        results = await search_tool.search("人工智能", num_results=3)
        
        if results:
            print(f"找到 {len(results)} 个搜索结果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title}")
                print(f"     URL: {result.url}")
                print(f"     摘要: {result.snippet[:100]}...")
            print("✅ 搜索功能正常")
            return True
        else:
            print("❌ 未找到搜索结果")
            return False
    except Exception as e:
        print(f"❌ 搜索功能失败: {e}")
        return False


async def test_vector_store():
    """测试向量存储"""
    print("\n=== 测试向量存储 ===")
    try:
        from services.llama_index_service import llama_index_service
        
        # 测试查询
        result = llama_index_service.query_index("测试查询")
        print(f"向量查询结果: {result[:100]}...")
        print("✅ 向量存储功能正常")
        return True
    except Exception as e:
        print(f"❌ 向量存储功能失败: {e}")
        return False


async def test_agent():
    """测试完整智能体"""
    print("\n=== 测试完整智能体 ===")
    try:
        from angent import DeepSearchAgent
        
        agent = DeepSearchAgent()
        status = agent.get_status()
        
        print(f"智能体状态: {status['status']}")
        print(f"模型信息: {status['model_info']}")
        print(f"功能特性: {', '.join(status['features'])}")
        
        print("✅ 智能体初始化成功")
        return True
    except Exception as e:
        print(f"❌ 智能体初始化失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("Deep Search Agent 功能测试")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        print("请创建.env文件并设置API密钥")
        return
    
    # 运行各项测试
    tests = [
        test_config,
        test_llm,
        test_search,
        test_vector_store,
        test_agent
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("测试结果总结:")
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖")


if __name__ == "__main__":
    asyncio.run(main())
