from src.mcp.server import MCPServer
from src.tool import Terminate
from src.tool.sentiment import SentimentTool
from src.tool.web_search import WebSearch


class SentimentServer(MCPServer):
    def __init__(self, name: str = "SentimentServer"):
        super().__init__(name)

    def _initialize_standard_tools(self) -> None:
        self.tools.update(
            {
                "sentiment_tool": SentimentTool(),
                "web_search": WebSearch(),
                "terminate": Terminate(),
            }
        )
