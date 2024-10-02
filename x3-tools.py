import curses
import os
import json
import subprocess
import threading
import time
from datetime import datetime

CONFIG_FILE = 'multitool_config.json'
BACKUP_CONFIG_FILE = 'multitool_config_backup.json'
LOG_FILE = 'installation_log.txt'

# Updated tool categories with top 10 popular software based on feedback
FILTERED_TOOLS = {
    "Daily Use": [
        "Google Chrome", "Visual Studio Code", "Notepad++", "Slack", "Zoom", 
        "VLC Media Player", "Spotify", "LibreOffice", "7-Zip", "Adobe Acrobat Reader",
        "Firefox", "Opera", "Brave", "Thunderbird", "OneNote",
        "Microsoft Teams", "Dropbox", "GIMP", "Paint.NET", "KeePass"
    ],
    "OSINT": [
        "Maltego", "Wireshark", "Shodan", "Spiderfoot", "Recon-ng", 
        "Metasploit", "Burp Suite", "OWASP ZAP", "theHarvester", "Nmap",
        "Amass", "Nikto", "Sherlock", "Censys", "Photon", 
        "Netcraft", "FOCA", "SpiderFoot", "Datasploit", "GHunt"
    ],
    "Cybersecurity": [
        "Kali Linux", "Metasploit", "Wireshark", "OpenVPN", "KeePass", 
        "VeraCrypt", "Gpg4win", "Burp Suite", "OWASP ZAP", "Tor Browser",
        "John the Ripper", "Hydra", "Hashcat", "Aircrack-ng", "Responder",
        "SQLMap", "Snort", "Suricata", "Nessus", "Maltego"
    ],
    "System Tools": [
        "Sysinternals Suite", "Process Hacker", "Autoruns", "Process Explorer", 
        "HWiNFO", "CrystalDiskInfo", "Speccy", "GPU-Z", "Core Temp", "TCPView",
        "PowerToys", "Everything", "CCleaner", "TreeSize", "Recuva", 
        "Rufus", "DiskGenius", "HWMonitor", "FastCopy", "Ventoy"
    ],
    "Communication": [
        "Discord", "Telegram", "Signal", "WhatsApp", "Skype", 
        "Slack", "Zoom", "Microsoft Teams", "Google Meet", "Viber",
        "WeChat", "Facebook Messenger", "Line", "Wire", "ICQ",
        "Tox", "Mattermost", "Element", "Trillian", "Jitsi"
    ],
    "Multimedia": [
        "VLC Media Player", "Spotify", "Audacity", "GIMP", "Inkscape", 
        "Blender", "Adobe Premiere Pro", "DaVinci Resolve", "Shotcut", "OBS Studio",
        "Krita", "HandBrake", "KMPlayer", "Media Player Classic", "Avidemux",
        "FL Studio", "Mixxx", "Ableton Live", "Cubase", "Kdenlive"
    ],
    "Office & PDF": [
        "LibreOffice", "Microsoft Word", "Adobe Acrobat Reader", "Foxit Reader", 
        "SumatraPDF", "Google Docs", "WPS Office", "OnlyOffice", "Notion", "Evernote",
        "Dropbox Paper", "Zoho Docs", "OneDrive", "Quip", "SoftMaker Office",
        "Nitro PDF", "Scribus", "Polaris Office", "AbiWord", "Mendeley"
    ]
}


# Mapping readable tool names to actual winget package names
TOOL_MAP = {
   
    "Google Chrome": "Google.Chrome", "Visual Studio Code": "Microsoft.VisualStudioCode", 
    "Notepad++": "Notepad++.Notepad++", "Slack": "SlackTechnologies.Slack", 
    "Zoom": "Zoom.Zoom", "VLC Media Player": "VideoLAN.VLC", 
    "Spotify": "Spotify.Spotify", "LibreOffice": "TheDocumentFoundation.LibreOffice", 
    "7-Zip": "7zip.7zip", "Adobe Acrobat Reader": "Adobe.AdobeAcrobatReaderDC",
    
    # Additional Daily Use tools
    "Firefox": "Mozilla.Firefox", "Opera": "Opera.Opera", "Brave": "Brave.Brave", 
    "Thunderbird": "Mozilla.Thunderbird", "OneNote": "Microsoft.OneNote", 
    "Microsoft Teams": "Microsoft.Teams", "Dropbox": "Dropbox.Dropbox", 
    "GIMP": "GIMP.GIMP", "Paint.NET": "dotPDNLLC.Paint.NET", "KeePass": "DominikReichl.KeePass",

    # OSINT Tools
    "Maltego": "Paterva.MaltegoCE", "Wireshark": "WiresharkFoundation.Wireshark", 
    "Shodan": "Shodan.Shodan", "Spiderfoot": "Spiderfoot.Spiderfoot", "Recon-ng": "Recon-ng.Recon-ng", 
    "Metasploit": "Rapid7.Metasploit", "Burp Suite": "PortSwigger.BurpSuiteFree", 
    "OWASP ZAP": "OWASP.ZAP", "theHarvester": "theHarvester.theHarvester", "Nmap": "Nmap.Nmap",

    # Cybersecurity Tools
    "Kali Linux": "KaliLinux.KaliLinux", "OpenVPN": "OpenVPNTechnologies.OpenVPN", 
    "Tor Browser": "TorProject.TorBrowser", "John the Ripper": "Openwall.JohnTheRipper", 
    "Hydra": "THC-Hydra.Hydra", "Hashcat": "hashcat.hashcat",

    # Additional mappings for other tools
    "Process Hacker": "wj32.ProcessHacker", "HWiNFO": "Realix.HWiNFO", 
    "Discord": "Discord.Discord", "Telegram": "Telegram.TelegramDesktop",
    "OBS Studio": "OBSProject.OBSStudio", "Krita": "Krita.Krita",
    "Foxit Reader": "FoxitSoftware.FoxitReader", "Evernote": "Evernote.Evernote"
}



def load_config():      
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def backup_config(config):
    with open(BACKUP_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def log_message(message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"{datetime.now()}: {message}\n")

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

def center_text(window, text, row, width, color_pair):
    """Center text in the window."""
    for i, line in enumerate(text.split('\n')):
        x_position = max(0, (width - len(line)) // 2)
        window.addstr(row + i, x_position, line[:width-1], color_pair)

def draw_columns(stdscr, categories, current_option, selected_options, start_row, start_col, col_width, col_height):
    """Draw tool categories and tools in columns with improved feedback."""
    for col, (category, tools) in enumerate(categories.items()):
        stdscr.addstr(start_row, start_col + col * col_width, category, curses.color_pair(1) | curses.A_BOLD)
        for row, tool in enumerate(tools):
            if row >= col_height:
                break
            marker = ">" if (col, row) == current_option else ("[x]" if (col, row) in selected_options else "[ ]")
            color = curses.color_pair(2) if (col, row) == current_option else curses.color_pair(1)
            stdscr.addstr(start_row + row + 1, start_col + col * col_width, f"{marker} {tool}"[:col_width-1], color)
        if col < len(categories) - 1:
            stdscr.vline(start_row, start_col + (col + 1) * col_width - 1, '|', col_height + 1)

def confirm_action(stdscr, prompt):
    """Ask for user confirmation with a clean interface."""
    stdscr.clear()
    stdscr.addstr(2, 2, prompt, curses.color_pair(1))
    stdscr.addstr(4, 2, "Press 'y' to confirm, 'n' to cancel", curses.color_pair(1))
    stdscr.refresh()
    key = stdscr.getch()
    return key == ord('y')

def install_tools(stdscr, selected_tools, config):
    """Install selected tools using winget and provide detailed feedback."""
    failed_installs = []
    for tool in selected_tools:
        try:
            package_name = TOOL_MAP.get(tool, tool)
            stdscr.clear()
            stdscr.addstr(2, 2, f"Installing {tool} ({package_name})...", curses.color_pair(1))
            stdscr.refresh()

            # Simulated download and installation process
            total_size = 100  # Placeholder for file size in MB
            downloaded = 0
            start_time = time.time()

            process = subprocess.Popen(
                ["winget", "install", package_name, "--accept-source-agreements", "--accept-package-agreements"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    stdscr.addstr(4, 2, output.strip(), curses.color_pair(1))
                    stdscr.refresh()

                # Simulate download progress
                downloaded += 5  # Simulate 5 MB download increments
                elapsed_time = time.time() - start_time
                speed = downloaded / elapsed_time  # MB/s

                if downloaded < total_size:
                    percentage = (downloaded / total_size) * 100
                    remaining_time = (total_size - downloaded) / speed if speed > 0 else 0
                    stdscr.addstr(6, 2, f"Downloaded: {downloaded:.2f} MB / {total_size} MB", curses.color_pair(1))
                    stdscr.addstr(7, 2, f"Progress: {percentage:.2f}% | Speed: {speed:.2f} MB/s | ETA: {remaining_time:.2f}s", curses.color_pair(1))
                    stdscr.refresh()

            if process.returncode == 0:
                stdscr.addstr(9, 2, f"Successfully installed {tool}", curses.color_pair(1))
            else:
                raise Exception(process.stderr.read())

        except Exception as e:
            failed_installs.append(tool)
            stdscr.addstr(9, 2, f"Failed to install {tool}: {e}", curses.color_pair(1))

        stdscr.refresh()
        stdscr.getch()  # Wait for user input before continuing

    if failed_installs:
        config['last_action'] = f"Failed to install: {', '.join(failed_installs)}"
    else:
        config['last_action'] = f"Installed {', '.join(selected_tools)} successfully"
    
    save_config(config)
    show_message(stdscr, "Installation process completed.", curses.color_pair(1))

def run_concurrent_install(stdscr, selected_tools, config):
    """Run installations concurrently using threads for faster execution."""
    threads = []
    for tool in selected_tools:
        thread = threading.Thread(target=install_tools, args=(stdscr, [tool], config))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    stdscr.addstr(10, 2, "All installations completed.", curses.color_pair(1))
    stdscr.refresh()
    stdscr.getch()

def show_message(stdscr, message, color_pair):
    """Display a message in a separate window."""
    height, width = stdscr.getmaxyx()
    message_window = curses.newwin(5, width - 4, (height - 5) // 2, 2)
    message_window.attron(curses.color_pair(1))
    message_window.box()
    message_window.attroff(curses.color_pair(1))
    message_window.addstr(2, 2, message, color_pair)
    message_window.refresh()
    stdscr.getch()

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

        stdscr.attron(curses.color_pair(1))
        stdscr.border()
        stdscr.attroff(curses.color_pair(1))

        # Draw title and developer info
        title_height = len(title.split('\n'))
        center_text(stdscr, title, 1, width, curses.color_pair(1))
        dev_info_height = len(developer_info.split('\n'))
        center_text(stdscr, developer_info, title_height + 1, width, curses.color_pair(1))

        col_start_row = title_height + dev_info_height + 3
        col_start_col = 2
        col_width = width // len(categories)
        col_height = height - col_start_row - 4
        draw_columns(stdscr, categories, current_option, selected_options, col_start_row, col_start_col, col_width, col_height)

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
        elif key == 10:  # Enter to select/unselect
            if current_option in selected_options:
                selected_options.remove(current_option)
            else:
                selected_options.add(current_option)
        elif key == ord('i'):  # Install selected tools
            confirm_install = confirm_action(stdscr, "Are you sure you want to install the selected tools?")
            if confirm_install:
                run_concurrent_install(stdscr, [categories[list(categories.keys())[col]][row] for col, row in selected_options], config)
                selected_options.clear()

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
