import os
import secrets
import sys

from pathlib import Path

import mcp
from mcp.server import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp.resources.types import FileResource


class StaticTokenVerifier(TokenVerifier):
    def __init__(self, token: str):
        super().__init__()
        self._token = token


    async def verify_token(self, token: str) -> AccessToken | None:
        if token == self._token:
            return AccessToken(
                token='',
                client_id='',
                scopes=[],
            )
        else:
            return None


def create_server(**kwargs) -> FastMCP:
    token = os.environ.get('MCP_ACCESS_TOKEN', '')
    if not token:
        token = 'rnd-' + secrets.token_urlsafe(32)
        print(f'Using random access token: {token}')

    mcp = FastMCP(
        'Files as Resources',
        json_response=True,
        auth=AuthSettings(
            issuer_url='http://localhost',
            resource_server_url='http://localhost',
        ),
        token_verifier=StaticTokenVerifier(token),
        **kwargs
    )
    return mcp


def add_files(mcp: FastMCP):
    prefix = 'data/'
    for file in Path(prefix).rglob('*'):
        if file.is_dir():
            continue
        if file.name.startswith('.'):
            continue

        name = file.as_posix()[len(prefix):]
        print(f'Adding file: {name}')
        mcp.add_resource(FileResource(
            uri=f'file:///{name}',
            name=name,
            path=file.absolute(),
        ))


if __name__ == "__main__":
    mcp = create_server(host='0.0.0.0')
    add_files(mcp)
    mcp.run(transport="streamable-http")
