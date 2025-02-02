from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session
from lib.database import SessionLocal
import sys
import os
import asyncio
from dotenv import load_dotenv

console = Console()

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        console.print(f"[red]Error connecting to database: {e}[/red]")
        sys.exit(1)

def list_pending_kyc(db: Session):
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
        
        result = radiolist_dialog(
            title="Pending KYC Requests",
            text="Select a user to view details:",
            values=choices
        ).run()

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

def list_approved_users(db: Session):
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
        
        result = radiolist_dialog(
            title="Approved Users",
            text="Select a user to view details:",
            values=choices
        ).run()

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

def approve_kyc(db: Session):
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
        
        result = radiolist_dialog(
            title="Select User for KYC Approval",
            text="Choose a user to approve KYC:",
            values=choices
        ).run()

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

def show_backend_wallet(db: Session):
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
        
        result = radiolist_dialog(
            title="Backend Wallet Information",
            text="System wallet details:",
            values=choices
        ).run()

    except Exception as e:
        console.print(f"[red]Error showing backend wallet info: {e}[/red]")

def regenerate_backend_wallet(db: Session):
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
        
        result = radiolist_dialog(
            title="Regenerate Backend Wallet",
            text="Are you sure you want to proceed?",
            values=warning_choices
        ).run()
        
        if not result:
            return
            
        confirmation = prompt("Type 'CONFIRM' to proceed with wallet regeneration: ")
        if confirmation != "CONFIRM":
            return
            
        wallet_service = BackendWalletService()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        wallet = loop.run_until_complete(wallet_service.create_wallet())
        loop.close()
        
        success_choices = [(
            "success",
            f"Wallet Regenerated Successfully\n"
            f"New Address: {wallet['address']}"
        )]
        
        radiolist_dialog(
            title="Success",
            text="Backend wallet has been regenerated:",
            values=success_choices
        ).run()
        
    except Exception as e:
        console.print(f"[red]Error regenerating backend wallet: {e}[/red]")

def send_eth_to_user(db: Session):
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
        
        result = radiolist_dialog(
            title="Select User to Send ETH",
            text="Choose a user:",
            values=choices
        ).run()

        if result and isinstance(result, User):
            amount = prompt("Enter amount of ETH to send: ")
            try:
                float(amount)  # Validate amount is a number
            except ValueError:
                console.print("[red]Invalid amount. Please enter a number.[/red]")
                return

            confirmation = prompt(f"Type 'CONFIRM' to send {amount} ETH to @{result.username} ({result.wallet_address}): ")
            if confirmation != "CONFIRM":
                return

            from backend.app.services.backend_wallet import BackendWalletService
            wallet_service = BackendWalletService()
            wallet_info = wallet_service.get_wallet_info()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tx_hash = loop.run_until_complete(wallet_service.sendTransaction(
                wallet_info['private_key'],
                result.wallet_address,
                amount
            ))
            loop.close()

            console.print("[green]Transaction sent successfully![/green]")
            console.print(f"[green]Transaction hash: {tx_hash}[/green]")
            console.print(f"[green]View on explorer: https://sepolia.basescan.org/tx/{tx_hash}[/green]")
    except Exception as e:
        console.print(f"[red]Error sending ETH: {e}[/red]")

def delete_user(db: Session):
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
        
        result = radiolist_dialog(
            title="Select User to Delete",
            text="Choose a user to delete:",
            values=choices
        ).run()

        if result and isinstance(result, User):
            confirmation = prompt(f"Type 'DELETE' to confirm deletion of @{result.username}: ")
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

def main_menu():
    """Display the main menu and handle user input."""
    while True:
        choices = [
            ("list_pending", "List Pending KYC"),
            ("approve", "Approve KYC"),
            ("list_approved", "List Approved Users"),
            ("wallet_info", "Backend Wallet"),
            ("regenerate", "Regenerate Wallet"),
            ("send_eth", "Send ETH"),
            ("delete", "Delete User"),
            ("exit", "Exit")
        ]
        
        result = radiolist_dialog(
            title="Base Hackathon Admin CLI",
            text="Select an operation:",
            values=choices
        ).run()
        
        if not result or result == "exit":
            console.print("[yellow]Goodbye![/yellow]")
            break
            
        db = get_db()
        
        try:
            if result == "list_pending":
                list_pending_kyc(db)
            elif result == "approve":
                approve_kyc(db)
            elif result == "list_approved":
                list_approved_users(db)
            elif result == "wallet_info":
                show_backend_wallet(db)
            elif result == "regenerate":
                regenerate_backend_wallet(db)
            elif result == "send_eth":
                send_eth_to_user(db)
            elif result == "delete":
                delete_user(db)
        finally:
            db.close()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
