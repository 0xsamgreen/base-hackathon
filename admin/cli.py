from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session
from lib.database import SessionLocal
import sys

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

def approve_kyc(db: Session):
    """Approve KYC for a selected user."""
    try:
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
            result.kyc = True
            db.commit()
            console.print(f"[green]KYC approved for user {result.telegram_id}[/green]")
        else:
            console.print("[yellow]Operation cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error approving KYC: {e}[/red]")

def main_menu():
    """Display the main menu and handle user input."""
    while True:
        console.print("\n[bold blue]Admin CLI Menu[/bold blue]")
        console.print("1. List Pending KYC")
        console.print("2. Approve KYC")
        console.print("3. List Approved Users")
        console.print("4. Exit")
        
        choice = prompt("Select an option: ")
        
        db = get_db()
        
        if choice == "1":
            list_pending_kyc(db)
        elif choice == "2":
            approve_kyc(db)
        elif choice == "3":
            list_approved_users(db)
        elif choice == "4":
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
