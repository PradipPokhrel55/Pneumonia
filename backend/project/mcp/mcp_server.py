from fastmcp import FastMCP
from services.cnn_service import predict_pneumonia
from services.rag_service import generate_answer

mcp = FastMCP()

@mcp.tool()
def ask_pneumonia_assistant(query: str) -> str:
    return generate_answer(query)

@mcp.tool()
def predict_xray(image_file) -> dict:
    return predict_pneumonia(image_file)