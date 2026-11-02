import gradio as gr
from main import app as fastapi_app
import uvicorn

# Create a blank Gradio interface to satisfy Hugging Face's requirements
demo = gr.Blocks()
with demo:
    gr.Markdown("# TripSmith API is Live!")

# Mount the FastAPI app onto Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)