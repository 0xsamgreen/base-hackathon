import asyncio
import json
import os
from typing import Dict, Any

class NFTDeployService:
    @staticmethod
    async def deploy_contract(name: str, symbol: str) -> Dict[str, str]:
        """Deploy NFT contract using the TypeScript deployment service."""
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct path to the CLI script
        cli_path = os.path.join(current_dir, 'nft_deploy_cli.js')
        
        # Prepare the command
        cmd = [
            'node',
            cli_path,
            'deploy',
            name,
            symbol
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
            raise Exception(f"Error deploying NFT contract: {error_msg}")
            
        # Parse the JSON response
        result = json.loads(stdout.decode().strip())
        return result
        
    @staticmethod
    async def verify_deployment(contract_address: str) -> bool:
        """Verify NFT contract deployment."""
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct path to the CLI script
        cli_path = os.path.join(current_dir, 'nft_deploy_cli.js')
        
        # Prepare the command
        cmd = [
            'node',
            cli_path,
            'verify',
            contract_address
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
            raise Exception(f"Error verifying NFT contract: {error_msg}")
            
        # Parse the JSON response
        result = json.loads(stdout.decode().strip())
        return result.get('isValid', False)
