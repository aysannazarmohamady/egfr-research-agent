import gradio as gr

def research_agent_interface():
    return "Hello! I'm your Research Agent!"

if __name__ == "__main__":
    demo = gr.Interface(
        fn=research_agent_interface,
        inputs="text",
        outputs="text",
        title="Research Agent",
        description="AI-powered research agent"
    )
    demo.launch()
