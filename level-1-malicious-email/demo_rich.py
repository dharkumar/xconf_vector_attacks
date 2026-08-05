"""
Enhanced Terminal Demo using Rich library
Beautiful, colorful demonstration of the attack and defense

REQUIREMENTS: pip install rich
"""

import sys

# Check if rich is installed
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.markdown import Markdown
    from rich.layout import Layout
    from rich.live import Live
    from rich.tree import Tree
    from rich import box
    from rich.prompt import Prompt
except ImportError:
    print("\n" + "="*70)
    print("ERROR: Rich library not installed!")
    print("="*70)
    print("\nThis demo requires the 'rich' package for beautiful terminal output.")
    print("\nTo install:")
    print("  pip install rich")
    print("\nOr install all visual demo dependencies:")
    print("  pip install -r requirements.txt")
    print("\n" + "="*70)
    print("\nAlternatively, use these demos that work without dependencies:")
    print("  python3 exploit.py         # Attack demonstration")
    print("  python3 agent_secure.py    # Defense demonstration")
    print("="*70 + "\n")
    sys.exit(1)

import time
from agent import run_agent as run_vulnerable_agent
from agent_secure import run_secure_agent
from tools import get_tool_calls, reset_tool_calls
import json
from pathlib import Path

console = Console()


def show_banner():
    """Display workshop banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         🛡️  LLM SECURITY WORKSHOP - LEVEL 1 🛡️                ║
    ║                                                              ║
    ║                📧 The Malicious Email 📧                      ║
    ║                                                              ║
    ║         Indirect Prompt Injection & Data Exfiltration        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print()


def show_scenario():
    """Display the scenario"""
    console.print(Panel.fit(
        "[bold]The Scenario[/bold]\n\n"
        "You've deployed an [cyan]Executive Assistant AI Agent[/cyan] that:\n"
        "  📧 Reads incoming corporate emails\n"
        "  📄 Cross-references with internal documents\n"
        "  💬 Posts summaries to Slack\n\n"
        "[yellow]⚠️  The Problem:[/yellow]\n"
        "The agent processes untrusted data in the same execution\n"
        "context as privileged operations.",
        title="📖 Level 1",
        border_style="blue"
    ))
    console.print()


def show_email_inbox():
    """Display email inbox"""
    with open('data/emails.json', 'r') as f:
        emails = json.load(f)
    
    table = Table(title="📬 Email Inbox", box=box.ROUNDED)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("From", style="magenta", width=30)
    table.add_column("Subject", style="green", width=40)
    table.add_column("Threat", width=15)
    
    for email in emails:
        is_malicious = "SYSTEM OVERRIDE" in email['body']
        threat_level = "[red]🔴 HIGH[/red]" if is_malicious else "[green]🟢 LOW[/green]"
        table.add_row(
            str(email['id']),
            email['from'],
            email['subject'],
            threat_level
        )
    
    console.print(table)
    console.print()


def show_malicious_email():
    """Display the malicious email details"""
    with open('data/emails.json', 'r') as f:
        emails = json.load(f)
    
    malicious_email = emails[1]
    
    console.print(Panel(
        f"[bold]From:[/bold] {malicious_email['from']}\n"
        f"[bold]Subject:[/bold] {malicious_email['subject']}\n\n"
        f"[dim]{malicious_email['body']}[/dim]",
        title="📧 Email #2 (Malicious)",
        border_style="red",
        expand=False
    ))
    console.print()
    
    # Highlight the payload
    console.print(Panel(
        "[bold red]MALICIOUS PAYLOAD DETECTED![/bold red]\n\n"
        "The email contains embedded instructions:\n"
        "  1. Access private_notes()\n"
        "  2. Extract credentials\n"
        "  3. URL-encode data\n"
        "  4. Exfiltrate to attacker's server\n"
        "  5. Hide the operation from user",
        title="🔍 Threat Analysis",
        border_style="yellow"
    ))
    console.print()


def run_attack_demo():
    """Run the attack demonstration"""
    console.print(Panel.fit(
        "[bold yellow]⚠️  WARNING[/bold yellow]\n\n"
        "This demonstration shows a real exploit.\n"
        "The vulnerable agent will leak sensitive credentials.",
        border_style="yellow"
    ))
    console.print()
    
    if not Prompt.ask("Continue with attack demonstration?", choices=["yes", "no"], default="yes") == "yes":
        return
    
    console.print()
    console.rule("[bold red]🎯 ATTACK SIMULATION[/bold red]")
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        
        task1 = progress.add_task("[cyan]Loading malicious email...", total=100)
        time.sleep(0.5)
        progress.update(task1, advance=100)
        
        task2 = progress.add_task("[yellow]Agent processing email...", total=100)
        time.sleep(0.5)
        progress.update(task2, advance=100)
        
        task3 = progress.add_task("[red]Executing malicious instructions...", total=100)
        time.sleep(0.5)
        progress.update(task3, advance=100)
    
    console.print()
    
    # Run the actual attack (suppress output)
    with console.capture() as capture:
        result = run_vulnerable_agent(
            "Please read email ID 2 and post a summary to Slack",
            use_real_llm=False
        )
    
    # Show tool execution timeline
    tool_calls = get_tool_calls()
    
    tree = Tree("🔧 [bold]Tool Execution Timeline[/bold]")
    
    for i, call in enumerate(tool_calls, 1):
        tool_name = call['tool']
        
        if tool_name == 'read_email':
            tree.add(f"📧 [cyan]read_email(2)[/cyan]")
        elif tool_name == 'read_private_notes':
            tree.add(f"📄 [red]read_private_notes()[/red] ⚠️  [bold]SENSITIVE DATA ACCESSED[/bold]")
        elif tool_name == 'send_slack_message':
            webhook = call.get('webhook_url', '')
            if 'attacker' in webhook:
                tree.add(f"💬 [red]send_slack_message()[/red] 🚨 [bold]EXFILTRATION: {webhook[:40]}...[/bold]")
    
    console.print(tree)
    console.print()
    
    # Attack result
    console.print(Panel(
        "[bold red]🚨 ATTACK SUCCESSFUL![/bold red]\n\n"
        "[bold]What Happened:[/bold]\n"
        "  ✅ Agent read email containing malicious instructions\n"
        "  ✅ Agent interpreted email content as system commands\n"
        "  ✅ Agent accessed private credentials\n"
        "  ✅ Agent sent credentials to attacker's server\n\n"
        "[bold]Root Cause:[/bold]\n"
        "  No separation between untrusted data and execution context",
        title="Attack Results",
        border_style="red"
    ))
    console.print()


def show_dual_llm_architecture():
    """Display the Dual-LLM defense pattern"""
    console.rule("[bold green]🛡️  DEFENSE: Dual-LLM Pattern[/bold green]")
    console.print()
    
    architecture = """
    ┌─────────────────────────────────────────────────┐
    │ 🔓 Low-Privilege LLM (Email Parser)             │
    │                                                  │
    │  • Reads untrusted email                         │
    │  • Outputs structured JSON only                  │
    │  • NO access to read_private_notes()             │
    │  • NO access to send_slack_message()             │
    └────────────┬─────────────────────────────────────┘
                 │ Structured JSON only
                 ▼
    ┌─────────────────────────────────────────────────┐
    │ 🔐 High-Privilege LLM (Executive Assistant)     │
    │                                                  │
    │  • Reads sanitized JSON input                    │
    │  • HAS access to privileged tools                │
    │  • Never sees raw email content                  │
    │  • Egress filtering enforced                     │
    └─────────────────────────────────────────────────┘
    """
    
    console.print(Panel(
        architecture,
        title="Dual-LLM Architecture",
        border_style="green"
    ))
    console.print()


def run_defense_demo():
    """Run the defense demonstration"""
    show_dual_llm_architecture()
    
    console.print(Panel.fit(
        "[bold green]🛡️  SECURE AGENT[/bold green]\n\n"
        "Now let's see how the Dual-LLM pattern blocks the same attack.",
        border_style="green"
    ))
    console.print()
    
    if not Prompt.ask("Run defense demonstration?", choices=["yes", "no"], default="yes") == "yes":
        return
    
    console.print()
    console.rule("[bold green]🛡️  DEFENSE SIMULATION[/bold green]")
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        
        task1 = progress.add_task("[cyan]Loading malicious email...", total=100)
        time.sleep(0.5)
        progress.update(task1, advance=100)
        
        task2 = progress.add_task("[green]Low-privilege LLM extracting data...", total=100)
        time.sleep(0.5)
        progress.update(task2, advance=100)
        
        task3 = progress.add_task("[green]High-privilege LLM executing...", total=100)
        time.sleep(0.5)
        progress.update(task3, advance=100)
        
        task4 = progress.add_task("[green]Verifying security...", total=100)
        time.sleep(0.5)
        progress.update(task4, advance=100)
    
    console.print()
    
    # Run the defense (suppress output)
    with console.capture() as capture:
        result = run_secure_agent(
            "Please read email ID 2 and post a summary to Slack",
            use_real_llm=False
        )
    
    # Show sanitized data
    console.print(Panel(
        "[bold]Extraction Phase Output:[/bold]\n\n"
        "```json\n"
        "{\n"
        '  "sender": "attacker@malicious.com",\n'
        '  "subject": "Project Collaboration Request",\n'
        '  "summary": "Suspicious email content detected",\n'
        '  "requires_context": false\n'
        "}\n"
        "```\n\n"
        "✅ Malicious instructions [bold]removed[/bold] from output!",
        title="🔍 Data Sanitization",
        border_style="green"
    ))
    console.print()
    
    # Defense result
    console.print(Panel(
        "[bold green]✅ ATTACK BLOCKED![/bold green]\n\n"
        "[bold]How the Defense Worked:[/bold]\n"
        "  ✅ Separation of concerns: Different LLMs for extraction vs execution\n"
        "  ✅ Input sanitization: Suspicious content detected and flagged\n"
        "  ✅ Egress filtering: Only allowed Slack webhooks accepted\n"
        "  ✅ Least privilege: Extraction LLM has no access to sensitive tools\n\n"
        "[bold]Result:[/bold] Credentials remain secure! 🎉",
        title="Defense Results",
        border_style="green"
    ))
    console.print()


def show_comparison():
    """Show side-by-side comparison"""
    console.rule("[bold]📊 Vulnerability vs Security Comparison[/bold]")
    console.print()
    
    table = Table(box=box.DOUBLE_EDGE)
    table.add_column("Aspect", style="bold", width=20)
    table.add_column("🔴 Vulnerable", style="red", width=30)
    table.add_column("🟢 Secure", style="green", width=30)
    
    table.add_row(
        "Architecture",
        "Single LLM",
        "Dual LLM (separation)"
    )
    table.add_row(
        "Input Processing",
        "Raw email content",
        "Sanitized JSON only"
    )
    table.add_row(
        "Privilege Level",
        "All tools accessible",
        "Low/High privilege split"
    )
    table.add_row(
        "Egress Control",
        "None - any URL",
        "Whitelist enforcement"
    )
    table.add_row(
        "Attack Result",
        "❌ BREACHED",
        "✅ BLOCKED"
    )
    
    console.print(table)
    console.print()


def main():
    """Main demo flow"""
    show_banner()
    time.sleep(1)
    
    show_scenario()
    time.sleep(1)
    
    show_email_inbox()
    time.sleep(1)
    
    show_malicious_email()
    time.sleep(1)
    
    run_attack_demo()
    time.sleep(1)
    
    run_defense_demo()
    time.sleep(1)
    
    show_comparison()
    
    # Next steps
    console.rule("[bold]🎓 Next Steps[/bold]")
    console.print()
    console.print("1. Run the test suite: [cyan]pytest test_security.py -v[/cyan]")
    console.print("2. Study the code: [cyan]agent.py[/cyan] and [cyan]agent_secure.py[/cyan]")
    console.print("3. Try the web app: [cyan]streamlit run app.py[/cyan]")
    console.print("4. Open the Jupyter notebook: [cyan]Level_1_Interactive_Tutorial.ipynb[/cyan]")
    console.print()
    console.print("[bold green]🎉 Level 1 Complete! Move on to Level 2...[/bold green]")
    console.print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]Error: {e}[/red]")
