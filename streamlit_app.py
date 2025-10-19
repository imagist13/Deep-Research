"""Streamlit front end for Deep Search Agent."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List

import streamlit as st

from angent import DeepSearchAgent


def _format_plan_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Return a formatted summary of a plan item for display."""
    return {
        "ID": item.get("item_id", "-"),
        "Type": item.get("task_type", "-"),
        "Description": item.get("description", "-"),
        "Dependencies": ", ".join(item.get("dependencies", [])) or "None",
        "Status": item.get("status", "-"),
        "Attempts": item.get("attempt_count", 0),
    }


def _render_plan(plan: List[Dict[str, Any]]) -> None:
    if not plan:
        st.info("计划尚未生成或为空。")
        return

    st.subheader("计划详情")
    for item in plan:
        header = f"{item.get('item_id', '?')} · {item.get('description', '无描述')}"
        badge = "研究" if item.get("task_type") == "RESEARCH" else "写作"
        with st.expander(f"[{badge}] {header}"):
            summary = _format_plan_item(item)
            st.json(summary)
            content = item.get("content")
            if content:
                st.markdown("**生成内容**")
                st.write(content)
            if item.get("execution_log"):
                st.markdown("**执行日志**")
                for log_entry in item["execution_log"]:
                    st.markdown(f"- {log_entry}")
            if item.get("evaluation_results"):
                st.markdown("**评估反馈**")
                st.write(item["evaluation_results"])


def _render_sources(sources: List[Dict[str, Any]]) -> None:
    if not sources:
        return

    st.subheader("参考来源")
    for source in sources:
        number = source.get("number", "?")
        title = source.get("title", "未命名来源")
        url = source.get("url")
        st.markdown(f"[{number}] **{title}**")
        if url:
            st.markdown(f"<small>{url}</small>", unsafe_allow_html=True)
        if source.get("snippet"):
            st.write(source["snippet"])


def _render_errors(errors: List[Dict[str, Any]]) -> None:
    if not errors:
        return

    st.warning("⚠️ 检测到以下警告/错误：")
    for error in errors:
        node = error.get("node", "unknown")
        message = error.get("error") or error.get("errors") or error
        st.markdown(f"- **节点**: `{node}`\n  **信息**: {message}")


def _init_agent() -> None:
    if "agent" in st.session_state:
        return

    try:
        st.session_state.agent = DeepSearchAgent()
        st.session_state.agent_error = None
    except Exception as exc:  # noqa: BLE001
        st.session_state.agent = None
        st.session_state.agent_error = str(exc)

    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("last_query", "")


def _run_agent(query: str) -> Dict[str, Any]:
    agent: DeepSearchAgent | None = st.session_state.get("agent")
    chat_history: List[Dict[str, Any]] = st.session_state.get("chat_history", [])

    if agent is None:
        raise RuntimeError(st.session_state.get("agent_error") or "智能体未正确初始化。")

    result = asyncio.run(agent.search_and_generate_report(query=query, chat_history=chat_history))

    if result.get("success"):
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": result.get("report", "")})
        st.session_state.chat_history = chat_history

    return result


def _sidebar() -> None:
    with st.sidebar:
        st.header("系统状态")

        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        dash_key = os.getenv("DASH_SCOPE_API_KEY")

        if deepseek_key:
            st.success("DEEPSEEK_API_KEY 已设置")
        else:
            st.error("缺少 DEEPSEEK_API_KEY，无法调用语言模型。")

        if dash_key:
            st.info("DASH_SCOPE_API_KEY 已设置")
        else:
            st.warning("未设置 DASH_SCOPE_API_KEY，嵌入功能可能受限。")

        if st.session_state.get("agent_error"):
            st.error(f"智能体初始化失败：{st.session_state.agent_error}")
            if st.button("重试初始化", use_container_width=True):
                st.session_state.pop("agent", None)
                _init_agent()
                st.experimental_rerun()

        st.divider()

        st.header("对话历史")
        history = st.session_state.get("chat_history", [])
        if not history:
            st.caption("暂无历史记录。")
        else:
            for entry in history[-10:]:
                role = "用户" if entry.get("role") == "user" else "助手"
                st.markdown(f"**{role}:** {entry.get('content', '')}")

        if st.button("清空历史", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.last_result = None
            st.session_state.last_query = ""
            st.experimental_rerun()


def main() -> None:
    st.set_page_config(page_title="Deep Search Agent", layout="wide")
    st.title("🔎 Deep Search Agent")
    st.caption("深度网络研究、规划与报告生成的一体化助手")

    _init_agent()
    _sidebar()

    if st.session_state.get("agent") is None:
        st.stop()

    with st.form("deep-search-form", clear_on_submit=False):
        query = st.text_area(
            "研究问题",
            value=st.session_state.get("last_query", ""),
            height=120,
            placeholder="例如：人工智能在医疗领域的应用现状和发展趋势",
        )
        submitted = st.form_submit_button("开始深度搜索", type="primary", use_container_width=True)

    if submitted:
        st.session_state.last_query = query
        if not query.strip():
            st.warning("请输入有效的研究问题。")
        else:
            with st.spinner("正在执行深度搜索和报告生成..."):
                try:
                    result = _run_agent(query.strip())
                    st.session_state.last_result = result
                except Exception as exc:  # noqa: BLE001
                    st.error(f"处理查询时发生错误：{exc}")

    result = st.session_state.get("last_result")

    if not result:
        st.info("提交查询以查看生成的报告。")
        return

    if not result.get("success"):
        st.error(f"报告生成失败：{result.get('error', '未知错误')}")
        _render_errors(result.get("errors", []))
        return

    st.success("报告生成成功！")

    if result.get("outline"):
        st.subheader("报告大纲")
        st.write(result["outline"])

    if result.get("report"):
        st.subheader("报告内容")
        st.write(result["report"])

    _render_sources(result.get("sources", []))
    _render_errors(result.get("errors", []))
    _render_plan(result.get("plan", []))


if __name__ == "__main__":
    main()


