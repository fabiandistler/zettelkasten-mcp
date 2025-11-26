#!/usr/bin/env python
"""HTTP server wrapper for the Zettelkasten MCP server.

This module provides an HTTP/SSE transport layer for the MCP server,
enabling remote access via Cloudflare Tunnel or other HTTP proxies.
"""
import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, Request, Response, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from zettelkasten_mcp.config import config
from zettelkasten_mcp.models.db_models import init_db
from zettelkasten_mcp.server.mcp_server import ZettelkastenMcpServer
from zettelkasten_mcp.utils import setup_logging

logger = logging.getLogger(__name__)

# Session storage (in-memory for now, can be extended to Redis/DB)
sessions: Dict[str, dict] = {}


class InitializeRequest(BaseModel):
    """MCP initialize request model."""
    jsonrpc: str = "2.0"
    id: int | str
    method: str
    params: Optional[dict] = None


class ToolCallRequest(BaseModel):
    """MCP tool call request model."""
    jsonrpc: str = "2.0"
    id: int | str
    method: str
    params: dict


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan context manager for startup and shutdown events."""
        # Startup
        # Ensure directories exist
        notes_dir = config.get_absolute_path(config.notes_dir)
        notes_dir.mkdir(parents=True, exist_ok=True)
        db_dir = config.get_absolute_path(config.database_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        try:
            logger.info(f"Using SQLite database: {config.get_db_url()}")
            init_db()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            sys.exit(1)

        # Create MCP server instance
        try:
            logger.info("Initializing Zettelkasten MCP server")
            mcp_server = ZettelkastenMcpServer()
            app.state.mcp_server = mcp_server
            logger.info("Zettelkasten MCP server ready")
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
            sys.exit(1)

        yield

        # Shutdown (if needed in future)
        logger.info("Shutting down Zettelkasten MCP server")

    app = FastAPI(
        title="Zettelkasten MCP Server",
        description="HTTP/SSE transport for Zettelkasten MCP",
        version=config.server_version,
        lifespan=lifespan,
    )

    # CORS configuration - restrict in production!
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """Root endpoint with server info."""
        return {
            "name": config.server_name,
            "version": config.server_version,
            "protocol": "MCP",
            "transports": ["http", "sse"],
            "status": "ready"
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.post("/mcp")
    async def mcp_endpoint(
        request: Request,
        mcp_session_id: Optional[str] = Header(None, alias="Mcp-Session-Id"),
    ):
        """
        Main MCP endpoint for JSON-RPC messages.

        Supports both regular HTTP and SSE upgrade for streaming responses.
        """
        # Get MCP server from app state
        mcp_server = request.app.state.mcp_server

        # Parse the request body
        try:
            body = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse request body: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")

        # Validate JSON-RPC format
        if not isinstance(body, dict) or "jsonrpc" not in body:
            raise HTTPException(status_code=400, detail="Invalid JSON-RPC request")

        # Handle session
        if not mcp_session_id:
            mcp_session_id = str(uuid.uuid4())
            sessions[mcp_session_id] = {"created_at": asyncio.get_event_loop().time()}

        # Process the MCP request
        method = body.get("method")
        request_id = body.get("id")
        params = body.get("params", {})

        logger.info(f"MCP request: method={method}, id={request_id}, session={mcp_session_id}")

        try:
            # Handle initialize
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                        },
                        "serverInfo": {
                            "name": config.server_name,
                            "version": config.server_version,
                        },
                    },
                }
                return JSONResponse(
                    response,
                    headers={"Mcp-Session-Id": mcp_session_id}
                )

            # Handle tools/list
            elif method == "tools/list":
                # Use FastMCP's built-in list_tools() method
                tools_result = await mcp_server.mcp.list_tools()

                # Convert to MCP protocol format
                tools = []
                for tool in tools_result.tools:
                    tools.append({
                        "name": tool.name,
                        "description": tool.description or f"Zettelkasten tool: {tool.name}",
                        "inputSchema": tool.inputSchema or {
                            "type": "object",
                            "properties": {},
                        }
                    })

                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    },
                }
                return JSONResponse(response, headers={"Mcp-Session-Id": mcp_session_id})

            # Handle tools/call
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})

                logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

                # Execute the tool
                result = await execute_tool(mcp_server, tool_name, tool_args)

                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    },
                }
                return JSONResponse(response, headers={"Mcp-Session-Id": mcp_session_id})

            else:
                raise HTTPException(status_code=400, detail=f"Unknown method: {method}")

        except Exception as e:
            logger.error(f"Error processing MCP request: {e}", exc_info=True)
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e),
                },
            }
            return JSONResponse(error_response, status_code=500)

    return app


async def execute_tool(mcp_server: ZettelkastenMcpServer, tool_name: str, args: dict) -> str:
    """Execute a tool on the MCP server using FastMCP's call_tool method."""
    try:
        # Use FastMCP's built-in call_tool method
        # This returns a list of TextContent objects
        result = await mcp_server.mcp.call_tool(tool_name, args)

        # result is a list of TextContent objects: [TextContent(text='...')]
        if isinstance(result, list) and len(result) > 0:
            first_item = result[0]
            if hasattr(first_item, 'text'):
                return first_item.text
            else:
                return str(first_item)
        elif isinstance(result, str):
            return result
        else:
            # Fallback: convert to string
            return str(result)

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        raise ValueError(f"Error executing tool {tool_name}: {str(e)}")


def main():
    """Run the HTTP server."""
    import argparse
    import uvicorn

    # Parse arguments
    parser = argparse.ArgumentParser(description="Zettelkasten MCP HTTP Server")
    parser.add_argument(
        "--host",
        default=os.getenv("HTTP_HOST", "127.0.0.1"),
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("HTTP_PORT", "8080")),
        help="Port to bind to"
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("ZETTELKASTEN_LOG_LEVEL", "INFO"),
        help="Logging level"
    )
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    logger.info(f"Starting Zettelkasten MCP HTTP server on {args.host}:{args.port}")

    # Create and run the app
    app = create_app()
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level.lower(),
    )


if __name__ == "__main__":
    main()
