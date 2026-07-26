"""Command-line entry point."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .capsule import compile_capsule
from .gateway import DataHubMcpGateway, FixtureGateway
from .render import write_capsule


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Compile DataHub evidence into safe agent context.")
    result.add_argument("--query", required=True)
    result.add_argument("--budget", type=int, default=6000)
    result.add_argument("--fixture", type=Path)
    result.add_argument("--output", type=Path, default=Path("output"))
    result.add_argument("--mcp-command", default="uvx")
    result.add_argument("--mcp-package", default="mcp-server-datahub@latest")
    return result


async def run(args: argparse.Namespace) -> int:
    if args.fixture:
        capsule = await compile_capsule(FixtureGateway.from_path(args.fixture), args.query, args.budget)
    else:
        async with DataHubMcpGateway(args.mcp_command, [args.mcp_package]) as gateway:
            capsule = await compile_capsule(gateway, args.query, args.budget)
    markdown, manifest = write_capsule(capsule, args.output)
    print(f"entities={capsule.entity_count} quarantined={capsule.quarantined_count} truncated={capsule.truncated}")
    print(f"context={markdown.resolve()}")
    print(f"manifest={manifest.resolve()}")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(run(parser().parse_args())))


if __name__ == "__main__":
    main()

