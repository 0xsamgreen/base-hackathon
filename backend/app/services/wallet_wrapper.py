import asyncio
import json
import os

class WalletService:
    def __init__(self):
        self.node_path = os.path.join(os.path.dirname(__file__), 'wallet_cli.js')

    async def _call_node(self, method: str, *args) -> dict:
        try:
            # Call Node.js script with method and arguments
            cmd = ['node', self.node_path, method] + list(map(str, args))
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            stderr_output = stderr.decode() if stderr else None
            stdout_output = stdout.decode() if stdout else None
            
            if proc.returncode != 0:
                print(f"Node.js stderr: {stderr_output}")
                print(f"Node.js stdout: {stdout_output}")
                raise Exception(f"Node.js error: {stderr_output}")
            
            try:
                return json.loads(stdout_output)
            except json.JSONDecodeError as e:
                print(f"JSON decode error. Raw output: {stdout_output}")
                raise
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from Node.js")

    async def create_wallet(self):
        return await self._call_node('createWallet')

    async def get_wallet_provider(self, private_key: str):
        return await self._call_node('getWalletProvider', private_key)

    async def send_transaction(self, private_key: str, to: str, amount: str):
        return await self._call_node('sendTransaction', private_key, to, amount)
