import logging
import sys

from src.mcp.server import MCPServer
from src.tool import Terminate
from src.tool.hot_money import HotMoneyTool


logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stderr)])


class HotMoneyServer(MCPServer):
    def __init__(self, name: str = "HotMoneyServer"):
        super().__init__(name)

    def _initialize_standard_tools(self) -> None:
        self.tools.update(
            {
                "hot_money_tool": HotMoneyTool(),
                "terminate": Terminate(),
            }
        )
