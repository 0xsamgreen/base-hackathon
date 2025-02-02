"""Backend wallet service for managing the system wallet."""
import os
from dotenv import load_dotenv, set_key
from .wallet_wrapper import WalletService
import asyncio

class BackendWalletService:
    def __init__(self):
        self.wallet_service = WalletService()
        self.env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
        load_dotenv(self.env_path)

    def get_wallet_info(self):
        """Get backend wallet info from env."""
        return {
            'address': os.getenv('BACKEND_WALLET_ADDRESS'),
            'private_key': os.getenv('BACKEND_WALLET_PRIVATE_KEY')
        }

    def has_wallet(self):
        """Check if backend wallet exists."""
        wallet = self.get_wallet_info()
        return bool(wallet['address'] and wallet['private_key'])

    async def create_wallet(self):
        """Create a new backend wallet."""
        wallet = await self.wallet_service.create_wallet()
        
        # Update .env file
        with open(self.env_path, 'r') as f:
            env_content = f.read()
            
        # Remove old wallet entries if they exist
        lines = env_content.splitlines()
        lines = [line for line in lines if not line.startswith(('BACKEND_WALLET_ADDRESS=', 'BACKEND_WALLET_PRIVATE_KEY='))]
        
        # Add new wallet info
        lines.extend([
            f"BACKEND_WALLET_ADDRESS={wallet['address']}",
            f"BACKEND_WALLET_PRIVATE_KEY={wallet['privateKey']}"
        ])
        
        # Update .env file
        set_key(self.env_path, "BACKEND_WALLET_ADDRESS", wallet['address'])
        set_key(self.env_path, "BACKEND_WALLET_PRIVATE_KEY", wallet['privateKey'])
        return wallet

    async def get_balance(self):
        """Get backend wallet balance."""
        wallet = self.get_wallet_info()
        if not wallet['address']:
            return None
        
        result = await self.wallet_service.get_wallet_client(wallet['private_key'])
        return result.get('balance', '0')

    async def sendTransaction(self, private_key: str, to: str, amount: str):
        """Send a transaction."""
        return await self.wallet_service.send_transaction(private_key, to, amount)

async def initialize_backend_wallet():
    """Initialize backend wallet if it doesn't exist."""
    service = BackendWalletService()
    if not service.has_wallet():
        print("Creating backend wallet...")
        wallet = await service.create_wallet()
        print(f"Backend wallet created: {wallet['address']}")
    return service
