import curses
import os
import json
import subprocess
from datetime import datetime

CONFIG_FILE = 'multitool_config.json'

# Mapping readable tool names to actual winget package names
TOOL_MAP = {
    "Git": "Git.Git",
    "Python3": "Python.Python.3",
    "Vim": "Vim.Vim",
    "Htop": "Htop.Htop",
    "Tmux": "GnuWin32.Tmux",
    "Chrome": "Google.Chrome",
    "VSCode": "Microsoft.VisualStudioCode",
    "7-Zip": "7zip.7zip",
    "Wireshark": "WiresharkFoundation.Wireshark",
    "Nmap": "Nmap.Nmap",
    "Metasploit": "Rapid7.Metasploit",
    "Burp Suite": "PortSwigger.BurpSuiteFree",
    "OWASP ZAP": "OWASP.ZAP",
    "Maltego": "Maltego.Maltego",
    "Kali Linux": "KaliLinux.KaliLinux",
    "Tor Browser": "TorProject.TorBrowser",
    "KeePass": "DominikReichl.KeePass",
    "VeraCrypt": "IDRIX.VeraCrypt",
    "Gpg4win": "Gpg4win.Gpg4win",
    "OpenVPN": "OpenVPNTechnologies.OpenVPN",
    "PuTTY": "PuTTY.PuTTY",
    "FileZilla": "FileZilla.FileZilla",
    "Notepad++": "Notepad++.Notepad++",
    "Postman": "Postman.Postman",
    "Docker": "Docker.DockerDesktop",
    "VirtualBox": "Oracle.VirtualBox",
    "VMware Workstation": "VMware.WorkstationPlayer",
    "Sysinternals Suite": "Microsoft.SysinternalsSuite",
    "Process Hacker": "wj32.ProcessHacker",
    "Autoruns": "Microsoft.SysinternalsAutoruns",
    "Process Explorer": "Microsoft.SysinternalsProcessExplorer",
    "TCPView": "Microsoft.SysinternalsTCPView",
    "BgInfo": "Microsoft.SysinternalsBgInfo",
    "Zoom": "Zoom.Zoom",
    "Slack": "SlackTechnologies.Slack",
    "Discord": "Discord.Discord",
    "Telegram": "Telegram.TelegramDesktop",
    "Signal": "OpenWhisperSystems.Signal",
    "WhatsApp": "WhatsApp.WhatsApp",
    "Skype": "Microsoft.Skype",
    "TeamViewer": "TeamViewer.TeamViewer",
    "AnyDesk": "AnyDeskSoftwareGmbH.AnyDesk",
    "VLC": "VideoLAN.VLC",
    "Spotify": "Spotify.Spotify",
    "Audacity": "Audacity.Audacity",
    "GIMP": "GIMP.GIMP",
    "Inkscape": "Inkscape.Inkscape",
    "Blender": "BlenderFoundation.Blender",
    "LibreOffice": "TheDocumentFoundation.LibreOffice",
    "Foxit Reader": "FoxitSoftware.FoxitReader",
    "SumatraPDF": "SumatraPDF.SumatraPDF"
}

# All tools categorized
FILTERED_TOOLS = {
    "Daily Use": [
        "Chrome", "VSCode", "7-Zip", "Notepad++", "Slack", "Zoom", "VLC", "Spotify", "LibreOffice",
        "Git", "Python3", "Vim", "Htop", "Tmux", "Postman", "Docker", "FileZilla"
    ],
    "OSINT": [
        "Maltego", "Tor Browser", "Wireshark", "Nmap", "Metasploit", "Burp Suite", "OWASP ZAP",
        "Chrome", "Firefox"
    ],
    "Cybersecurity": [
        "Kali Linux", "KeePass", "VeraCrypt", "Gpg4win", "OpenVPN", "PuTTY", "FileZilla", "Docker",
        "VirtualBox", "VMware Workstation", "Wireshark", "Nmap", "Metasploit", "Burp Suite", "OWASP ZAP"
    ],
    "System Tools": [
        "Sysinternals Suite", "Process Hacker", "Autoruns", "Process Explorer", "TCPView", "BgInfo"
    ],
    "Communication": [
        "Discord", "Telegram", "Signal", "WhatsApp", "Skype", "TeamViewer", "AnyDesk"
    ],
    "Multimedia": [
        "VLC", "Spotify", "Audacity", "GIMP", "Inkscape", "Blender"
    ],
    "Office & PDF": [
        "LibreOffice", "Foxit Reader", "SumatraPDF"
    ]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Cyan for everything
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Inverted for highlighting

def center_text(window, text, row, width, color_pair):
    for i, line in enumerate(text.split('\n')):
        x_position = max(0, (width - len(line)) // 2)
        window.addstr(row + i, x_position, line[:width-1], color_pair)

def draw_columns(stdscr, categories, current_option, selected_options, start_row, start_col, col_width, col_height):
    for col, (category, tools) in enumerate(categories.items()):
        stdscr.addstr(start_row, start_col + col * col_width, category, curses.color_pair(1) | curses.A_BOLD)
        for row, tool in enumerate(tools):
            if row >= col_height:
                break
            marker = ">" if (col, row) == current_option else ("[x]" if (col, row) in selected_options else "[ ]")
            color = curses.color_pair(2) if (col, row) == current_option else curses.color_pair(1)
            stdscr.addstr(start_row + row + 1, start_col + col * col_width, f"{marker} {tool}"[:col_width-1], color)

def main(stdscr):
    config = load_config()
    curses.curs_set(0)
    init_colors()

    title = """
██╗  ██╗██████╗       ████████╗ ██████╗  ██████╗ ██╗     ███████╗
╚██╗██╔╝╚════██╗      ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
 ╚███╔╝  █████╔╝█████╗   ██║   ██║   ██║██║   ██║██║     ███████╗
 ██╔██╗  ╚═══██╗╚════╝   ██║   ██║   ██║██║   ██║██║     ╚════██║
██╔╝ ██╗██████╔╝         ██║   ╚██████╔╝╚██████╔╝███████╗███████║
╚═╝  ╚═╝╚═════╝          ╚═╝    ╚═════╝  ╚══════╝╚══════╝╚══════╝
    """

    developer_info = f"""
X3 Tools v1.0.0
Developed by X3NIDE
GitHub.com/mubbashirulislam
Your Ultimate Tool Installation Assistant for Windows
Licensed under MIT License
Copyright © {datetime.now().year} X3NIDE
"""

    categories = FILTERED_TOOLS
    current_option = (0, 0)
    selected_options = set()

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Draw border
        stdscr.attron(curses.color_pair(1))
        stdscr.border()
        stdscr.attroff(curses.color_pair(1))

        # Draw title
        title_height = len(title.split('\n'))
        center_text(stdscr, title, 1, width, curses.color_pair(1))

        # Draw developer info
        dev_info_height = len(developer_info.split('\n'))
        center_text(stdscr, developer_info, title_height + 1, width, curses.color_pair(1))

        # Draw columns
        col_start_row = title_height + dev_info_height + 3
        col_start_col = 2
        col_width = width // len(categories)
        col_height = height - col_start_row - 4
        draw_columns(stdscr, categories, current_option, selected_options, col_start_row, col_start_col, col_width, col_height)

        # Draw status bar
        status = f"Selected tools: {len(selected_options)} | Last action: {config.get('last_action', 'None')}"
        stdscr.addstr(height - 3, 1, status[:width - 2], curses.color_pair(1) | curses.A_REVERSE)
        help_text = "Use arrow keys to navigate, Enter to select, 'i' to install, 'q' to quit"
        stdscr.addstr(height - 2, 1, help_text[:width - 2], curses.color_pair(1))

        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_UP:
            current_option = (current_option[0], max(0, current_option[1] - 1))
        elif key == curses.KEY_DOWN:
            current_option = (current_option[0], min(len(categories[list(categories.keys())[current_option[0]]]) - 1, current_option[1] + 1))
        elif key == curses.KEY_LEFT:
            current_option = ((current_option[0] - 1) % len(categories), min(current_option[1], len(categories[list(categories.keys())[(current_option[0] - 1) % len(categories)]]) - 1))
        elif key == curses.KEY_RIGHT:
            current_option = ((current_option[0] + 1) % len(categories), min(current_option[1], len(categories[list(categories.keys())[(current_option[0] + 1) % len(categories)]]) - 1))
        elif key == 10:  # Enter key to select/unselect tools
            if current_option in selected_options:
                selected_options.remove(current_option)
            else:
                selected_options.add(current_option)
        elif key == ord('i'):  # 'i' to install selected tools
            install_tools(stdscr, [categories[list(categories.keys())[col]][row] for col, row in selected_options], config)

        stdscr.refresh()

def install_tools(stdscr, selected_tools, config):
    failed_installs = []
    for tool in selected_tools:
        try:
            package_name = TOOL_MAP.get(tool, tool)  # Get actual winget package name or use the tool name if not found
            stdscr.clear()
            stdscr.addstr(2, 2, f"Installing {tool} ({package_name})...", curses.color_pair(1))
            stdscr.refresh()

            # Run winget install
            result = subprocess.run(["winget", "install", package_name], capture_output=True, text=True)
            
            # Check if the install command was successful
            if result.returncode == 0:
                stdscr.addstr(4, 2, f"Successfully installed {tool}", curses.color_pair(1))
            else:
                raise Exception(result.stderr)  # Raise an exception to handle the failure

        except Exception as e:
            failed_installs.append(tool)
            stdscr.addstr(4, 2, f"Failed to install {tool}: {e}", curses.color_pair(1))

        stdscr.refresh()
        stdscr.getch()  # Wait for user input before continuing

    # Update the config with the last action
    if failed_installs:
        config['last_action'] = f"Failed to install: {', '.join(failed_installs)}"
    else:
        config['last_action'] = f"Installed {', '.join(selected_tools)} successfully"
    
    save_config(config)
    show_message(stdscr, "Installation process completed.", curses.color_pair(1))

def show_message(stdscr, message, color_pair):
    height, width = stdscr.getmaxyx()
    message_window = curses.newwin(5, width - 4, (height - 5) // 2, 2)
    message_window.attron(curses.color_pair(1))
    message_window.box()
    message_window.attroff(curses.color_pair(1))
    message_window.addstr(2, 2, message, color_pair)
    message_window.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
