import typer
import subprocess
from pathlib import Path
from rich import print
import shellingham
from jinja2 import Template

app = typer.Typer(help="LabCast CLI - Configure lab switches with Ansible")

def open_template():
    with open('template/inventory_template.j2', 'r') as f:
        template = f.read()
    return template

def render_inventory(template, devices, user, key_file, mgmt_port):
    jinja_template = Template(template)
    inventory_content = jinja_template.render(devices=devices, user=user, key_file=key_file, mgmt_port=mgmt_port)
    return inventory_content

@app.command()
def configure(ip: str = typer.Argument(..., help="Comma-separated list of IPs"),
    submask: str = typer.Argument(..., help="IPs subnet mask"),
    hostname: str = typer.Argument(..., help="Comma-separated list of hostnames"),
    user: str = typer.Option("admin", help="SSH/Ansible username"),
    key_file: str = typer.Option(
        "~/.ssh/id_rsa", help="SSH/Ansible private key file"),
    mgmt_port: str = typer.Option("gi14", help="Management port on the switch"),
    dry_run: bool = typer.Option(False, help="Only render inventory, do not run playbook")
    ):
    """
    Configure Ansible inventory and deploy config to lab switches.

    Example:
        labcast configure --ip 10.130.140.8,10.130.140.9 --submask 255.255.255.0 --hostname br-mac-lab-sw1,br-mac-lab-sw2
    """
    ip_list = [i.strip() for i in ip.split(",")]
    hostname_list = [h.strip() for h in hostname.split(",")]

    if len(ip_list) != len(hostname_list):
        print("[red]Error: The number of IPs must match the number of hostnames.[/red]")
        raise typer.Exit(code=1)
    
    devices = [{"ip": ip, "hostname": hn} for ip, hn in zip(ip_list, hostname_list)]
        
    # Render Ansible inventory template
    template = open_template()
    inventory_content = render_inventory(template, devices, user, key_file, mgmt_port)
        
    # Write Ansible inventory file
    inventory_path = Path("inventory.ini")
    inventory_path.write_text(inventory_content)
    print(f"[green]Ansible inventory written to {inventory_path}[/green]")
    
    if dry_run:
        print("[yellow]Dry run enabled, skipping Ansible playbook execution.[/yellow]")
        raise typer.Exit()
    

    


    

    
if __name__ == "__main__":
    app()
