"""
Gradio Web 应用
提供聊天机器人的 Web 界面
"""

import gradio as gr

from config import config
from chat_engine import ChatEngine
from prompts import get_mode_list


# 全局引擎实例
engine: ChatEngine = None


def initialize():
    """初始化引擎"""
    global engine
    if not config.validate():
        raise ValueError("配置验证失败")
    engine = ChatEngine()


def chat_response(message: str, history: list):
    """处理聊天响应（流式）"""
    if not message.strip():
        return "", history

    # 添加用户消息
    history = history + [{"role": "user", "content": message}]

    # 流式生成响应
    response = ""
    for chunk in engine.stream_chat(message):
        response += chunk
        yield "", history + [{"role": "assistant", "content": response}]


def change_mode(mode: str):
    """切换对话模式"""
    engine.change_mode(mode)
    return f"已切换到: {mode}"


def clear_chat():
    """清空对话"""
    engine.clear_history()
    return [], "对话已清空"


def export_chat():
    """导出对话"""
    content = engine.export_history()
    if not content:
        return "暂无对话记录"
    return content


def get_token_info():
    """获取 token 信息"""
    count = engine.get_token_count()
    return f"当前对话 Token: {count}"


def create_app():
    """创建 Gradio 应用"""
    initialize()

    with gr.Blocks(
        title="智能聊天机器人",
    ) as app:
        gr.Markdown("# 🤖 智能聊天机器人")
        gr.Markdown("支持多轮对话、流式输出、多种对话模式")

        with gr.Row():
            with gr.Column(scale=4):
                # 聊天区域
                chatbot = gr.Chatbot(
                    label="对话",
                    height=450,
                    elem_classes="chatbot",
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="输入消息",
                        placeholder="输入消息后按 Enter 发送...",
                        scale=4,
                        lines=2,
                    )
                    send_btn = gr.Button("发送", variant="primary", scale=1)

            with gr.Column(scale=1):
                # 控制面板
                gr.Markdown("### ⚙️ 设置")

                mode_dropdown = gr.Dropdown(
                    choices=get_mode_list(),
                    value="通用助手",
                    label="对话模式",
                )
                mode_status = gr.Textbox(
                    label="状态",
                    value="当前: 通用助手",
                    interactive=False,
                )

                gr.Markdown("---")

                clear_btn = gr.Button("🗑️ 清空对话")
                export_btn = gr.Button("📥 导出对话")

                token_info = gr.Textbox(
                    label="Token 统计",
                    value="当前对话 Token: 0",
                    interactive=False,
                )

                export_area = gr.Textbox(
                    label="导出内容",
                    lines=5,
                    visible=True,
                )

        # 事件绑定
        msg.submit(
            chat_response,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
        ).then(
            get_token_info,
            outputs=[token_info],
        )

        send_btn.click(
            chat_response,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
        ).then(
            get_token_info,
            outputs=[token_info],
        )

        mode_dropdown.change(
            change_mode,
            inputs=[mode_dropdown],
            outputs=[mode_status],
        )

        clear_btn.click(
            clear_chat,
            outputs=[chatbot, mode_status],
        ).then(
            get_token_info,
            outputs=[token_info],
        )

        export_btn.click(
            export_chat,
            outputs=[export_area],
        )

        # 使用说明
        gr.Markdown("""
        ---
        ### 使用说明
        - **对话模式**: 选择不同模式获得专业化回答
        - **流式输出**: 响应实时显示，无需等待
        - **导出对话**: 将对话记录导出为文本
        """)

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
        css="""
        .message { font-size: 16px; }
        .chatbot { min-height: 400px; }
        """,
    )
