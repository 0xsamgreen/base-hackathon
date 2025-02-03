from prompt_toolkit.shortcuts import PromptSession, radiolist_dialog
from prompt_toolkit.application import create_app_session
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session
from lib.database import SessionLocal
import sys
import os
import asyncio
from dotenv import load_dotenv

console = Console()
session = PromptSession()

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        console.print(f"[red]Error connecting to database: {e}[/red]")
        sys.exit(1)

async def list_pending_kyc(db: Session):
    """List all users with pending KYC."""
    try:
        from backend.app.models.user import User
        users = db.query(User).filter(User.kyc == False).all()
        
        if not users:
            choices = [(
                "no_users",
                "No Pending KYC Requests\n"
                "There are no users awaiting KYC verification."
            )]
        else:
            choices = [(user, f"@{user.username}\n"
                             f"Full Name: {user.full_name}\n"
                             f"Birthday: {user.birthday}\n"
                             f"Phone: {user.phone}\n"
                             f"Email: {user.email}\n"
                             f"Telegram ID: {user.telegram_id}")
                      for user in users]
        
        dialog = radiolist_dialog(
            title="Pending KYC Requests",
            text="Select a user to view details:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()

        if result and isinstance(result, User):
            console.print("\n[bold blue]Selected User Details[/bold blue]")
            console.print(f"Username: @{result.username}")
            console.print(f"Full Name: {result.full_name}")
            console.print(f"Birthday: {result.birthday}")
            console.print(f"Phone: {result.phone}")
            console.print(f"Email: {result.email}")
            console.print(f"Telegram ID: {result.telegram_id}")
            console.print(f"PIN: {result.pin}")

    except Exception as e:
        console.print(f"[red]Error listing users: {e}[/red]")

async def list_approved_users(db: Session):
    """List all users with approved KYC."""
    try:
        from backend.app.models.user import User
        users = db.query(User).filter(User.kyc == True).all()
        
        if not users:
            choices = [(
                "no_users",
                "No Approved Users\n"
                "There are no KYC-approved users in the system."
            )]
        else:
            choices = [(user, f"@{user.username}\n"
                             f"Full Name: {user.full_name}\n"
                             f"Wallet: {user.wallet_address}\n"
                             f"Telegram ID: {user.telegram_id}")
                      for user in users]
        
        dialog = radiolist_dialog(
            title="Approved Users",
            text="Select a user to view details:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()

        if result and isinstance(result, User):
            console.print("\n[bold blue]Selected User Details[/bold blue]")
            console.print(f"Username: @{result.username}")
            console.print(f"Full Name: {result.full_name}")
            console.print(f"Wallet Address: {result.wallet_address}")
            console.print(f"Telegram ID: {result.telegram_id}")
            console.print(f"Email: {result.email}")
            console.print(f"Phone: {result.phone}")

    except Exception as e:
        console.print(f"[red]Error listing approved users: {e}[/red]")

def check_server():
    """Check if the backend server is running."""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

async def approve_kyc(db: Session):
    """Approve KYC for a selected user."""
    try:
        if not check_server():
            console.print("[red]Error: Backend server is not running. Please start it with './dev.sh start'[/red]")
            return

        from backend.app.models.user import User
        users = db.query(User).filter(User.kyc == False).all()
        
        if not users:
            choices = [(
                "no_users",
                "No Pending KYC Requests\n"
                "There are no users awaiting KYC verification."
            )]
        else:
            choices = [(user, f"@{user.username}\n"
                             f"Full Name: {user.full_name}\n"
                             f"Telegram ID: {user.telegram_id}")
                      for user in users]
        
        dialog = radiolist_dialog(
            title="Select User for KYC Approval",
            text="Choose a user to approve KYC:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()

        if result and isinstance(result, User):
            # Use API to update KYC status with retries
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session = requests.Session()
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            response = session.patch(
                f"http://localhost:8000/api/v1/users/{result.telegram_id}",
                json={"kyc": True},
                timeout=10
            )
            if response.status_code == 200:
                user_data = response.json()
                console.print(f"[green]KYC approved for user {result.telegram_id}[/green]")
                if user_data.get("wallet_address"):
                    console.print(f"[green]Wallet generated: {user_data['wallet_address']}[/green]")
            else:
                console.print(f"[red]Error from API: {response.text}[/red]")
    except Exception as e:
        console.print(f"[red]Error approving KYC: {e}[/red]")

async def show_backend_wallet(db: Session):
    """Show backend wallet info."""
    try:
        # Load .env file from project root
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
        
        address = os.getenv('BACKEND_WALLET_ADDRESS')
        private_key = os.getenv('BACKEND_WALLET_PRIVATE_KEY')
        if not address or not private_key:
            choices = [(
                "no_wallet",
                "No Backend Wallet\n"
                "A new wallet will be created on next backend startup."
            )]
        else:
            choices = [(
                "wallet_info",
                f"Backend Wallet\n"
                f"Address: {address}\n"
                f"Private Key: {private_key}"
            )]
        
        dialog = radiolist_dialog(
            title="Backend Wallet Information",
            text="System wallet details:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()

    except Exception as e:
        console.print(f"[red]Error showing backend wallet info: {e}[/red]")

async def regenerate_backend_wallet(db: Session):
    """Regenerate the backend wallet after confirmation."""
    try:
        from backend.app.services.backend_wallet import BackendWalletService
        
        warning_choices = [(
            "confirm",
            "WARNING\n"
            "This will create a new backend wallet.\n"
            "The old wallet and its funds will no longer be accessible!\n\n"
            "Select to proceed with regeneration"
        )]
        
        dialog = radiolist_dialog(
            title="Regenerate Backend Wallet",
            text="Are you sure you want to proceed?",
            values=warning_choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()
        
        if not result:
            return
            
        confirmation = await session.prompt_async("Type 'CONFIRM' to proceed with wallet regeneration: ")
        if confirmation != "CONFIRM":
            return
            
        wallet_service = BackendWalletService()
        wallet = await wallet_service.create_wallet()
        
        success_choices = [(
            "success",
            f"Wallet Regenerated Successfully\n"
            f"New Address: {wallet['address']}"
        )]
        
        dialog = radiolist_dialog(
            title="Success",
            text="Backend wallet has been regenerated:",
            values=success_choices
        )
        
        with create_app_session():
            with patch_stdout():
                await dialog.run_async()
        
    except Exception as e:
        console.print(f"[red]Error regenerating backend wallet: {e}[/red]")

async def send_eth_to_user(db: Session):
    """Send ETH to an approved user."""
    try:
        from backend.app.models.user import User
        users = db.query(User).filter(User.kyc == True).all()
        
        if not users:
            choices = [(
                "no_users",
                "No Approved Users\n"
                "There are no KYC-approved users in the system."
            )]
        else:
            choices = [(user, f"@{user.username}\nWallet: {user.wallet_address}") 
                      for user in users if user.wallet_address]
            
            if not choices:
                choices = [(
                    "no_wallets",
                    "No Wallet Users\n"
                    "No approved users have wallets generated yet."
                )]
        
        dialog = radiolist_dialog(
            title="Select User to Send ETH",
            text="Choose a user:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()

        if result and isinstance(result, User):
            amount = await session.prompt_async("Enter amount of ETH to send: ")
            try:
                float(amount)  # Validate amount is a number
            except ValueError:
                console.print("[red]Invalid amount. Please enter a number.[/red]")
                return

            confirmation = await session.prompt_async(f"Type 'CONFIRM' to send {amount} ETH to @{result.username} ({result.wallet_address}): ")
            if confirmation != "CONFIRM":
                return

            from backend.app.services.backend_wallet import BackendWalletService
            wallet_service = BackendWalletService()
            wallet_info = wallet_service.get_wallet_info()

            tx_hash = await wallet_service.sendTransaction(
                wallet_info['private_key'],
                result.wallet_address,
                amount
            )

            console.print("[green]Transaction sent successfully![/green]")
            console.print(f"[green]Transaction hash: {tx_hash}[/green]")
            console.print(f"[green]View on explorer: https://sepolia.basescan.org/tx/{tx_hash}[/green]")
    except Exception as e:
        console.print(f"[red]Error sending ETH: {e}[/red]")

async def delete_user(db: Session):
    """Delete a user."""
    try:
        from backend.app.models.user import User
        users = db.query(User).all()
        
        if not users:
            choices = [(
                "no_users",
                "No Users Found\n"
                "There are no users in the system."
            )]
        else:
            choices = [(user, f"@{user.username}\n"
                             f"Telegram ID: {user.telegram_id}\n"
                             f"KYC: {'Yes' if user.kyc else 'No'}\n"
                             f"Wallet: {user.wallet_address or 'Not generated'}")
                      for user in users]
        
        dialog = radiolist_dialog(
            title="Select User to Delete",
            text="Choose a user to delete:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()

        if result and isinstance(result, User):
            confirmation = await session.prompt_async(f"Type 'DELETE' to confirm deletion of @{result.username}: ")
            if confirmation != "DELETE":
                return
            
            # Delete user's quiz completions first
            from backend.app.models.quiz import UserQuizCompletion
            db.query(UserQuizCompletion).filter(UserQuizCompletion.user_id == result.id).delete()
            
            # Delete the user
            db.delete(result)
            db.commit()
            
            console.print(f"[green]User {result.telegram_id} deleted successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error deleting user: {e}[/red]")

async def main_menu():
    """Display the main menu and handle user input."""
    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.patch_stdout import patch_stdout

    while True:
        choices = [
            ("list_pending", "List Pending KYC"),
            ("approve", "Approve KYC"),
            ("list_approved", "List Approved Users"),
            ("wallet_info", "Backend Wallet"),
            ("regenerate", "Regenerate Wallet"),
            ("send_eth", "Send ETH"),
            ("delete", "Delete User"),
            ("deploy_nft", "Deploy NFT Contract"),
            ("configure_nft", "Configure Quiz NFT Metadata"),
            ("exit", "Exit")
        ]
        
        dialog = radiolist_dialog(
            title="Base Hackathon Admin CLI",
            text="Select an operation:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()
        
        if not result or result == "exit":
            console.print("[yellow]Goodbye![/yellow]")
            break
            
        db = get_db()
        
        try:
            if result == "list_pending":
                await list_pending_kyc(db)
            elif result == "approve":
                await approve_kyc(db)
            elif result == "list_approved":
                await list_approved_users(db)
            elif result == "wallet_info":
                await show_backend_wallet(db)
            elif result == "regenerate":
                await regenerate_backend_wallet(db)
            elif result == "send_eth":
                await send_eth_to_user(db)
            elif result == "delete":
                await delete_user(db)
            elif result == "deploy_nft":
                await deploy_nft_contract(db)
            elif result == "configure_nft":
                await configure_nft_metadata(db)
        finally:
            db.close()

async def deploy_nft_contract(db: Session):
    """Deploy NFT contract for quiz completion badges."""
    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.patch_stdout import patch_stdout

    try:
        from backend.app.services.nft_deploy_wrapper import NFTDeployService
        import os

        # Check if contract is already deployed
        if os.getenv('NFT_CONTRACT_ADDRESS'):
            warning_choices = [(
                "warning",
                "WARNING: NFT Contract Already Deployed\n"
                f"Current contract address: {os.getenv('NFT_CONTRACT_ADDRESS')}\n\n"
                "Deploying a new contract will make the old one inaccessible.\n"
                "All previously minted NFTs will remain on the old contract."
            )]
            
            dialog = radiolist_dialog(
                title="NFT Contract Deployment",
                text="A contract is already deployed. Do you want to continue?",
                values=warning_choices
            )
            
            with create_app_session():
                with patch_stdout():
                    result = await dialog.run_async()
            
            if not result:
                return

        # Get contract details
        name = await session.prompt_async("Enter NFT collection name (e.g., 'Solar Panel Cleaning Badges'): ")
        if not name:
            return

        symbol = await session.prompt_async("Enter NFT symbol (e.g., 'CLEAN'): ")
        if not symbol:
            return

        confirmation = await session.prompt_async("Type 'DEPLOY' to proceed with contract deployment: ")
        if confirmation != "DEPLOY":
            return

        # Deploy contract
        nft_service = NFTDeployService()
        result = await nft_service.deploy_contract(name, symbol)

        # Verify deployment
        is_valid = await nft_service.verify_deployment(result['contractAddress'])
        if not is_valid:
            console.print("[red]Contract deployment could not be verified![/red]")
            return

        success_choices = [(
            "success",
            f"NFT Contract Deployed Successfully!\n\n"
            f"Contract Address: {result['contractAddress']}\n"
            f"Transaction Hash: {result['transactionHash']}\n\n"
            f"View on explorer: https://sepolia.basescan.org/tx/{result['transactionHash']}"
        )]

        dialog = radiolist_dialog(
            title="Success",
            text="Contract deployment details:",
            values=success_choices
        )
        
        with create_app_session():
            with patch_stdout():
                await dialog.run_async()

        console.print("\n[green]You can now configure NFT metadata for quizzes.[/green]")

    except Exception as e:
        console.print(f"[red]Error deploying NFT contract: {e}[/red]")

async def configure_nft_metadata(db: Session):
    """Configure NFT metadata for quiz completion."""
    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.patch_stdout import patch_stdout

    try:
        from backend.app.models.quiz import Quiz
        from backend.app.models.nft import NFTMetadata
        import json

        # Get available quizzes
        quizzes = db.query(Quiz).all()
        if not quizzes:
            console.print("[red]No quizzes found in the system.[/red]")
            return

        choices = [(quiz, f"{quiz.name} (Reward: {quiz.eth_reward_amount} ETH)")
                  for quiz in quizzes]

        dialog = radiolist_dialog(
            title="Configure Quiz NFT Metadata",
            text="Select a quiz to configure NFT metadata:",
            values=choices
        )
        
        with create_app_session():
            with patch_stdout():
                result = await dialog.run_async()

        if not result:
            return

        # Get existing metadata or prepare for new
        metadata = db.query(NFTMetadata).filter(NFTMetadata.quiz_id == result.id).first()
        
        console.print("\n[bold]Configuring NFT metadata for quiz:[/bold]")
        console.print(f"Quiz Name: {result.name}")
        console.print(f"ETH Reward: {result.eth_reward_amount}\n")
        
        if metadata:
            console.print("[yellow]Existing metadata found. Enter new values or press Enter to keep current values.[/yellow]\n")
        
        # Get metadata details
        name = await session.prompt_async("Enter NFT name (e.g., 'Solar Panel Cleaning Expert'): ",
                     default=metadata.name if metadata else "Solar Panel Cleaning Expert")
        if not name:
            return

        description = await session.prompt_async("Enter NFT description: ",
                           default=metadata.description if metadata else "Awarded for successfully completing the Solar Panel Cleaning quiz and demonstrating expertise in proper cleaning techniques.")
        if not description:
            return

        image_url = await session.prompt_async("Enter NFT image URL: ",
                          default=metadata.image_url if metadata else "https://example.com/solar-panel-expert.png")
        if not image_url:
            return

        # Default attributes for quiz completion
        attributes = {
            "quiz_name": result.name,
            "completion_date": "Dynamic",
            "score": "100%"
        }

        if metadata:
            # Update existing metadata
            metadata.name = name
            metadata.description = description
            metadata.image_url = image_url
            metadata.attributes = json.dumps(attributes)
        else:
            # Create new metadata
            metadata = NFTMetadata(
                quiz_id=result.id,
                name=name,
                description=description,
                image_url=image_url,
                attributes=json.dumps(attributes)
            )
            db.add(metadata)

        db.commit()
        
        console.print("\n[green]NFT metadata configured successfully![/green]")
        console.print("\n[bold]Configured Metadata:[/bold]")
        console.print(f"Name: {name}")
        console.print(f"Description: {description}")
        console.print(f"Image URL: {image_url}")
        console.print(f"Attributes: {attributes}")
        
        console.print("\n[yellow]Press Enter to return to main menu...[/yellow]")
        await session.prompt_async("")

    except Exception as e:
        console.print(f"[red]Error configuring NFT metadata: {e}[/red]")
        db.rollback()

def sync_main_menu():
    """Synchronous wrapper for the async main menu."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main_menu())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    finally:
        loop.close()

if __name__ == "__main__":
    sync_main_menu()
