import asyncio
import json
import os
from typing import Dict, Any

class NFTService:
    @staticmethod
    async def mint_nft(recipient_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Mint NFT using the TypeScript NFT service."""
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct path to the CLI script
        cli_path = os.path.join(current_dir, 'nft_cli.js')
        
        # Prepare the command
        cmd = [
            'node',
            cli_path,
            'mint',
            recipient_address,
            json.dumps(metadata)
        ]
        
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the process to complete
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            raise Exception(f"Error minting NFT: {error_msg}")
            
        # Parse the JSON response
        result = json.loads(stdout.decode().strip())
        return result
        
    @staticmethod
    async def get_token_uri(token_id: int) -> str:
        """Get token URI using the TypeScript NFT service."""
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct path to the CLI script
        cli_path = os.path.join(current_dir, 'nft_cli.js')
        
        # Prepare the command
        cmd = [
            'node',
            cli_path,
            'tokenUri',
            str(token_id)
        ]
        
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the process to complete
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            raise Exception(f"Error getting token URI: {error_msg}")
            
        return stdout.decode().strip()
