from . import server
import asyncio
import argparse

def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description='Gmail API MCP Server')
    parser.add_argument('--creds-file-path',
                        required=True,
                       help='OAuth 2.0 credentials file path')
    parser.add_argument('--token-path',
                        required=True,
                       help='File location to store and retrieve access and refresh tokens for application')
    parser.add_argument('--mode',
                        choices=['mcp', 'api'],
                        default='mcp',
                        help='Run mode (mcp or api)')
    parser.add_argument('--port',
                        type=int,
                        default=8000,
                        help='Port for API mode')
    
    args = parser.parse_args()
    asyncio.run(server.main(args.creds_file_path, args.token_path, args.mode, args.port))

# Optionally expose other important items at package level
__all__ = ['main', 'server']
