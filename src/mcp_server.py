"""Minimal MCP stdio server (no extra SDK).

Cursor (or any MCP client) can call the same named tools as the dashboard.
Protocol: JSON-RPC 2.0 over stdin/stdout, one message per line.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.catalog import TOOLS, run_tool  # noqa: E402
from src.nlp import route  # noqa: E402


def _tool_defs() -> list[dict[str, Any]]:
    defs = [
        {
            "name": "ask_data",
            "description": "Ask a natural-language question about the synthetic OMOP mart.",
            "inputSchema": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"],
            },
        }
    ]
    for name, spec in TOOLS.items():
        props: dict[str, Any] = {}
        if name == "lookup_patients":
            props = {
                "condition": {
                    "type": "string",
                    "description": "diabetes, hypertension, obesity, ckd, or influenza",
                },
                "county": {"type": "string"},
                "limit": {"type": "integer"},
            }
            
        if name == "build_research_cohort":
            props = {
                "condition": {
                    "type": "string",
                    "description": "diabetes, t2dm, hypertension, obesity, ckd, or influenza",
                },
                "county": {
                    "type": "string",
                    "description": "County name, e.g. Alameda",
                },
                "visit_type": {
                    "type": "string",
                    "description": "Use er for patients with at least one emergency visit",
                },
                "medication": {
                    "type": "string",
                    "description": "metformin or lisinopril",
                },
                "min_age": {
                    "type": "integer",
                    "description": "Minimum patient age",
                },
                "max_age": {
                    "type": "integer",
                    "description": "Maximum patient age",
                },
            }
                
        defs.append(
            {
                "name": name,
                "description": spec["description"],
                "inputSchema": {"type": "object", "properties": props},
            }
        )
    return defs


def _handle(msg: dict[str, Any]) -> dict[str, Any] | None:
    method = msg.get("method")
    msg_id = msg.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "omop-showcase", "version": "0.1.0"},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": _tool_defs()}}
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "ask_data":
                data = route(str(args.get("question") or ""))
            else:
                data = run_tool(name, **args)
            text = json.dumps(data, default=str, indent=2)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": text}]},
            }
        except Exception as exc:  # noqa: BLE001 — surface tool errors to the client
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "isError": True,
                    "content": [{"type": "text", "text": str(exc)}],
                },
            }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    if msg_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
        }
    return None


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        reply = _handle(msg)
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
