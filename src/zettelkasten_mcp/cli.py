#!/usr/bin/env python
"""CLI interface for Zettelkasten MCP server."""
import argparse
import logging
import os
import sys
from pathlib import Path

from zettelkasten_mcp.config import config
from zettelkasten_mcp.models.db_models import init_db
from zettelkasten_mcp.services.zettel_service import ZettelService
from zettelkasten_mcp.utils import setup_logging

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Zettelkasten CLI")
    parser.add_argument(
        "--notes-dir",
        help="Directory for storing note files",
        type=str,
        default=os.environ.get("ZETTELKASTEN_NOTES_DIR")
    )
    parser.add_argument(
        "--database-path",
        help="SQLite database file path",
        type=str,
        default=os.environ.get("ZETTELKASTEN_DATABASE_PATH")
    )
    parser.add_argument(
        "--log-level",
        help="Logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("ZETTELKASTEN_LOG_LEVEL", "INFO")
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # rebuild_index command
    subparsers.add_parser("rebuild_index", help="Rebuild the database index from Markdown files")

    # Add more commands here as needed

    return parser.parse_args()

def update_config(args):
    """Update the global config with command line arguments."""
    if args.notes_dir:
        config.notes_dir = Path(args.notes_dir)
    if args.database_path:
        config.database_path = Path(args.database_path)

def main():
    """Run the CLI."""
    args = parse_args()
    update_config(args)

    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Ensure directories exist
    notes_dir = config.get_absolute_path(config.notes_dir)
    notes_dir.mkdir(parents=True, exist_ok=True)
    db_dir = config.get_absolute_path(config.database_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    # Initialize database schema
    try:
        logger.info(f"Using SQLite database: {config.get_db_url()}")
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Initialize service
    zettel_service = ZettelService()

    # Execute command
    if args.command == "rebuild_index":
        try:
            logger.info("Rebuilding index...")
            zettel_service.rebuild_index()
            logger.info("Index rebuilt successfully.")
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()