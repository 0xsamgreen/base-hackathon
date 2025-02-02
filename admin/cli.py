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
        # We'll need to import the User model here
        from backend.app.models.user import User
        users = db.query(User).filter(User.kyc == False).all()
        
        if not users:
            console.print("[yellow]No pending KYC verifications found.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("ID", style="cyan")
        table.add_column("Telegram ID", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Full Name", style="green")
        table.add_column("Birthday", style="yellow")
        table.add_column("Phone", style="yellow")
        table.add_column("Email", style="yellow")
        table.add_column("Wallet Address", style="magenta")
        table.add_column("PIN", style="red")
        table.add_column("KYC Status", style="blue")

        for user in users:
            table.add_row(
                str(user.id),
                str(user.telegram_id),
                user.username or "N/A",
                user.full_name or "N/A",
                user.birthday or "N/A",
                user.phone or "N/A",
                user.email or "N/A",
                user.wallet_address or "N/A",
                user.pin or "N/A",
                "Pending" if not user.kyc else "Approved"
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing users: {e}[/red]")

def list_approved_users(db: Session):
    """List all users with approved KYC."""
    try:
        # Import User model
        from backend.app.models.user import User
        users = db.query(User).filter(User.kyc == True).all()
        
        if not users:
            console.print("[yellow]No approved users found.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("ID", style="cyan")
        table.add_column("Telegram ID", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Full Name", style="green")
        table.add_column("Birthday", style="yellow")
        table.add_column("Phone", style="yellow")
        table.add_column("Email", style="yellow")
        table.add_column("Wallet Address", style="magenta")
        table.add_column("PIN", style="red")
        table.add_column("KYC Status", style="blue")

        for user in users:
            table.add_row(
                str(user.id),
                str(user.telegram_id),
                user.username or "N/A",
                user.full_name or "N/A",
                user.birthday or "N/A",
                user.phone or "N/A",
                user.email or "N/A",
                user.wallet_address or "N/A",
                user.pin or "N/A",
                "Pending" if not user.kyc else "Approved"
            )

        console.print(table)
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
            console.print("[yellow]No pending KYC verifications found.[/yellow]")
            return

        choices = [(user, f"ID: {user.id}, Telegram: {user.telegram_id}, Username: {user.username}") 
                  for user in users]
        
        result = radiolist_dialog(
            title="Select User for KYC Approval",
            text="Choose a user to approve KYC:",
            values=choices
        ).run()

        if result:
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
        else:
            console.print("[yellow]Operation cancelled.[/yellow]")
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
            console.print("[yellow]No backend wallet found. One will be created on next backend startup.[/yellow]")
            return
            
        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Address", address)
        table.add_row("Private Key", private_key)
        
        console.print("\n[bold blue]Backend Wallet Info[/bold blue]")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error showing backend wallet info: {e}[/red]")

def regenerate_backend_wallet(db: Session):
    """Regenerate the backend wallet after confirmation."""
    try:
        from backend.app.services.backend_wallet import BackendWalletService
        
        console.print("[yellow]WARNING: This will create a new backend wallet. The old wallet and its funds will no longer be accessible![/yellow]")
        confirmation = prompt("Type 'CONFIRM' to proceed: ")
        
        if confirmation != "CONFIRM":
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
            
        wallet_service = BackendWalletService()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        wallet = loop.run_until_complete(wallet_service.create_wallet())
        loop.close()
        
        console.print("[green]Backend wallet regenerated successfully![/green]")
        console.print(f"[green]New wallet address: {wallet['address']}[/green]")
    except Exception as e:
        console.print(f"[red]Error regenerating backend wallet: {e}[/red]")

def send_eth_to_user(db: Session):
    """Send ETH to an approved user."""
    try:
        from backend.app.models.user import User
        users = db.query(User).filter(User.kyc == True).all()
        
        if not users:
            console.print("[yellow]No approved users found.[/yellow]")
            return

        choices = [(user, f"ID: {user.id}, Telegram: {user.telegram_id}, Address: {user.wallet_address}") 
                  for user in users if user.wallet_address]
        
        if not choices:
            console.print("[yellow]No users with wallet addresses found.[/yellow]")
            return

        result = radiolist_dialog(
            title="Select User to Send ETH",
            text="Choose a user:",
            values=choices
        ).run()

        if result:
            amount = prompt("Enter amount of ETH to send: ")
            try:
                float(amount)  # Validate amount is a number
            except ValueError:
                console.print("[red]Invalid amount. Please enter a number.[/red]")
                return

            confirmation = prompt(f"Type 'CONFIRM' to send {amount} ETH to {result.wallet_address}: ")
            if confirmation != "CONFIRM":
                console.print("[yellow]Operation cancelled.[/yellow]")
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
        else:
            console.print("[yellow]Operation cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error sending ETH: {e}[/red]")

def main_menu():
    """Display the main menu and handle user input."""
    while True:
        console.print("\n[bold blue]Admin CLI Menu[/bold blue]")
        console.print("1. List Pending KYC")
        console.print("2. Approve KYC")
        console.print("3. List Approved Users")
        console.print("4. Show Backend Wallet Info")
        console.print("5. Regenerate Backend Wallet")
        console.print("6. Send ETH to User")
        console.print("7. Exit")
        
        choice = prompt("Select an option: ")
        
        db = get_db()
        
        if choice == "1":
            list_pending_kyc(db)
        elif choice == "2":
            approve_kyc(db)
        elif choice == "3":
            list_approved_users(db)
        elif choice == "4":
            show_backend_wallet(db)
        elif choice == "5":
            regenerate_backend_wallet(db)
        elif choice == "6":
            send_eth_to_user(db)
        elif choice == "7":
            console.print("[yellow]Goodbye![/yellow]")
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")
        
        db.close()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
