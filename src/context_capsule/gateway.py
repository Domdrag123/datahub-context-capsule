"""Bounded read-only access to the official DataHub MCP server."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


MAX_FIXTURE_BYTES = 2_000_000
READ_ONLY_TOOLS = frozenset(
    {"search", "get_entities", "list_schema_fields", "get_lineage", "get_dataset_queries"}
)


class Gateway(Protocol):
    async def call(self, tool: str, arguments: dict[str, Any]) -> Any: ...


@dataclass
class FixtureGateway:
    payload: dict[str, Any]

    @classmethod
    def from_path(cls, path: Path) -> "FixtureGateway":
        if path.stat().st_size > MAX_FIXTURE_BYTES:
            raise ValueError("fixture exceeds the bounded input size")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("fixture root must be an object")
        return cls(payload)

    async def call(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool not in READ_ONLY_TOOLS:
            raise ValueError(f"mutation or unsupported tool refused: {tool}")
        assets = [item for item in self.payload.get("assets", []) if isinstance(item, dict)]
        if tool == "search":
            query = str(arguments.get("query", "")).casefold()
            return {
                "entities": [
                    {"urn": item.get("urn"), "name": item.get("name")}
                    for item in assets
                    if query in json.dumps(item, sort_keys=True).casefold()
                ]
            }
        urn = str(arguments.get("urn", ""))
        if tool == "get_entities":
            urns = set(arguments.get("urns", []))
            return {"entities": [item for item in assets if item.get("urn") in urns]}
        if tool == "list_schema_fields":
            return {"fields": self.payload.get("schemas", {}).get(urn, [])}
        if tool == "get_lineage":
            direction = str(arguments.get("direction", "upstream"))
            return {
                "relationships": self.payload.get("lineage", {}).get(urn, {}).get(direction, [])
            }
        return {"queries": self.payload.get("queries", {}).get(urn, [])}


class DataHubMcpGateway:
    def __init__(self, command: str, args: list[str]) -> None:
        self.command = command
        self.args = args
        self._stack: Any = None
        self._session: Any = None

    async def __aenter__(self) -> "DataHubMcpGateway":
        from contextlib import AsyncExitStack

        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        environment = {key: value for key, value in os.environ.items() if key != "TOOLS_IS_MUTATION_ENABLED"}
        environment["TOOLS_IS_MUTATION_ENABLED"] = "false"
        params = StdioServerParameters(command=self.command, args=self.args, env=environment)
        self._stack = AsyncExitStack()
        read_stream, write_stream = await self._stack.enter_async_context(stdio_client(params))
        self._session = await self._stack.enter_async_context(ClientSession(read_stream, write_stream))
        await self._session.initialize()
        available = {item.name for item in (await self._session.list_tools()).tools}
        missing = READ_ONLY_TOOLS - available
        if missing:
            await self._stack.aclose()
            raise RuntimeError(f"DataHub MCP server is missing tools: {sorted(missing)}")
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._stack is not None:
            await self._stack.aclose()

    async def call(self, tool: str, arguments: dict[str, Any]) -> Any:
        if tool not in READ_ONLY_TOOLS:
            raise ValueError(f"mutation or unsupported tool refused: {tool}")
        result = await self._session.call_tool(tool, arguments)
        if getattr(result, "isError", False):
            raise RuntimeError(f"DataHub MCP tool failed: {tool}")
        structured = getattr(result, "structuredContent", None)
        if structured is not None:
            return structured
        text = "\n".join(
            block.text
            for block in getattr(result, "content", [])
            if getattr(block, "type", None) == "text"
        )
        try:
            return json.loads(text) if text else {}
        except json.JSONDecodeError:
            return {"text": text}

