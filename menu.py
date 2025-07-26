#!/usr/bin/env python3
"""
Pharos Automation Bot Collection - Main Menu
Central launcher for all automation bots
Author: YetiDAO
"""

import os
import sys
import subprocess
import asyncio
from datetime import datetime
import pytz
from colorama import *

# Initialize colorama
init(autoreset=True)

# Timezone
wib = pytz.timezone('Asia/Jakarta')

class PharosMainMenu:
    def __init__(self):
        self.bots = {
            '1': {
                'name': 'Pharos Testnet Bot',
                'description': 'Core Pharos testnet automation',
                'file': 'bot1.py',
                'icon': '🚀'
            },
            '2': {
                'name': 'Gotchipus Bot',
                'description': 'Gotchipus protocol automation',
                'file': 'bot2.py',
                'icon': '🎮'
            },
            '3': {
                'name': 'OpenFi Bot',
                'description': 'OpenFi protocol automation',
                'file': 'bot3.py',
                'icon': '🔓'
            },
            '4': {
                'name': 'Brokex Bot',
                'description': 'Brokex trading automation',
                'file': 'bot4.py',
                'icon': '📈'
            },
            '5': {
                'name': 'Forswap Bot',
                'description': 'Forswap DEX automation',
                'file': 'bot5.py',
                'icon': '🔄'
            },
            '6': {
                'name': 'Primus Labs Social Bot',
                'description': 'Social platform automation',
                'file': 'bot6.py',
                'icon': '👥'
            },
            '7': {
                'name': 'Zenith Swap Bot',
                'description': 'Advanced swap and liquidity bot',
                'file': 'bot7.py',
                'icon': '⚡'
            },
            '8': {
                'name': 'AutoStaking Bot',
                'description': 'Smart staking operations',
                'file': 'bot8.py',
                'icon': '💰'
            },
            '9': {
                'name': 'AquaFlux RWAIFI Bot',
                'description': 'RWAIFI protocol automation',
                'file': 'bot9.py',
                'icon': '🌊'
            },
            '10': {
                'name': 'Pharos ENS Domain Bot',
                'description': 'ENS domain registration',
                'file': 'bot10.py',
                'icon': '🌐'
            },
            '11': {
                'name': 'Grandline nft Minting Bot',
                'description': 'Multi-collection NFT minting',
                'file': 'bot11.py',
                'icon': '🎨'
            }
        }

    def clear_terminal(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().astimezone(wib).strftime('%x %X %Z')
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        """Display welcome banner"""
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 80)
        print(Fore.GREEN + Style.BRIGHT + "    🚀 PHAROS AUTOMATION BOT COLLECTION 🚀")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Project    : Pharos Multi-Bot Launcher")
        print(Fore.YELLOW + Style.BRIGHT + "    🧑‍💻 Author     : YetiDAO Team")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Network    : Pharos Testnet Ecosystem")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────────────────────────")
        print(Fore.WHITE + Style.BRIGHT + "    📋 Choose from 11 specialized automation bots")
        print(Fore.GREEN + Style.BRIGHT + "    🎯 Each bot handles specific protocol operations")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────────────────────────")
        print(Fore.MAGENTA + Style.BRIGHT + "    🧬 Powered by YetiDAO | Complete Automation Suite 🚀")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 80 + "\n")

    def show_main_menu(self):
        """Display main bot selection menu"""
        print(f"{Fore.CYAN + Style.BRIGHT}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}                        {Fore.YELLOW + Style.BRIGHT}🤖 SELECT AUTOMATION BOT 🤖{Style.RESET_ALL}                         {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╠══════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
        
        # Display bots in two columns
        bot_keys = list(self.bots.keys())
        for i in range(0, len(bot_keys), 2):
            left_key = bot_keys[i]
            left_bot = self.bots[left_key]
            
            if i + 1 < len(bot_keys):
                right_key = bot_keys[i + 1]
                right_bot = self.bots[right_key]
                
                print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.GREEN + Style.BRIGHT}[{left_key:>2}]{Style.RESET_ALL} {left_bot['icon']} {left_bot['name']:<25} {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.GREEN + Style.BRIGHT}[{right_key:>2}]{Style.RESET_ALL} {right_bot['icon']} {right_bot['name']:<25} {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}     {Fore.YELLOW + Style.DIM}{left_bot['description']:<29}{Style.RESET_ALL} {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}     {Fore.YELLOW + Style.DIM}{right_bot['description']:<29}{Style.RESET_ALL} {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.GREEN + Style.BRIGHT}[{left_key:>2}]{Style.RESET_ALL} {left_bot['icon']} {left_bot['name']:<25} {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}                                   {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}     {Fore.YELLOW + Style.DIM}{left_bot['description']:<29}{Style.RESET_ALL} {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}                                   {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN + Style.BRIGHT}╠══════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}                            {Fore.RED + Style.BRIGHT}[0] Exit Menu{Style.RESET_ALL}                                {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print()

    def validate_bot_file(self, bot_file):
        """Check if bot file exists and is executable"""
        if not os.path.exists(bot_file):
            self.log(f"{Fore.RED}Error: {bot_file} not found!{Style.RESET_ALL}")
            return False
        
        if not os.access(bot_file, os.R_OK):
            self.log(f"{Fore.RED}Error: {bot_file} is not readable!{Style.RESET_ALL}")
            return False
        
        return True

    def launch_bot(self, bot_info):
        """Launch selected bot"""
        bot_file = bot_info['file']
        bot_name = bot_info['name']
        
        self.log(f"{Fore.GREEN}Launching {bot_name}...{Style.RESET_ALL}")
        
        if not self.validate_bot_file(bot_file):
            input("Press Enter to continue...")
            return False
        
        try:
            # Clear screen before launching bot
            self.clear_terminal()
            
            # Launch the bot using subprocess
            result = subprocess.run([sys.executable, bot_file], 
                                  cwd=os.getcwd(),
                                  check=False)
            
            # Bot has finished running
            self.clear_terminal()
            self.welcome()
            
            if result.returncode == 0:
                self.log(f"{Fore.GREEN}{bot_name} completed successfully{Style.RESET_ALL}")
            else:
                self.log(f"{Fore.YELLOW}{bot_name} exited with code {result.returncode}{Style.RESET_ALL}")
            
            return True
            
        except KeyboardInterrupt:
            self.log(f"{Fore.YELLOW}{bot_name} interrupted by user{Style.RESET_ALL}")
            return True
        except Exception as e:
            self.log(f"{Fore.RED}Error launching {bot_name}: {str(e)}{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return False

    def show_bot_info(self, bot_key):
        """Display detailed information about selected bot"""
        if bot_key not in self.bots:
            return
        
        bot = self.bots[bot_key]
        print(f"\n{Fore.CYAN + Style.BRIGHT}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}                           {Fore.YELLOW + Style.BRIGHT}📋 BOT INFORMATION 📋{Style.RESET_ALL}                            {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╠══════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Bot Name:{Style.RESET_ALL}    {bot['icon']} {Fore.GREEN + Style.BRIGHT}{bot['name']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Description:{Style.RESET_ALL} {Fore.YELLOW}{bot['description']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}File:{Style.RESET_ALL}        {Fore.CYAN}{bot['file']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}Status:{Style.RESET_ALL}      {'✅ Available' if self.validate_bot_file(bot['file']) else '❌ Not Found'}")
        print(f"{Fore.CYAN + Style.BRIGHT}╠══════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}  {Fore.GREEN + Style.BRIGHT}[Y]{Style.RESET_ALL} Launch Bot    {Fore.RED + Style.BRIGHT}[N]{Style.RESET_ALL} Back to Menu    {Fore.BLUE + Style.BRIGHT}[I]{Style.RESET_ALL} Bot Info          {Fore.CYAN + Style.BRIGHT}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN + Style.BRIGHT}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

    async def main(self):
        """Main menu loop"""
        while True:
            self.clear_terminal()
            self.welcome()
            self.show_main_menu()
            
            try:
                choice = input(f"{Fore.YELLOW + Style.BRIGHT}Select bot (1-11) or 0 to exit: {Style.RESET_ALL}").strip()
                
                if choice == '0':
                    self.log(f"{Fore.YELLOW}Exiting Pharos Bot Collection...{Style.RESET_ALL}")
                    break
                
                elif choice in self.bots:
                    while True:
                        self.clear_terminal()
                        self.welcome()
                        self.show_bot_info(choice)
                        
                        action = input(f"{Fore.CYAN + Style.BRIGHT}Your choice: {Style.RESET_ALL}").strip().upper()
                        
                        if action == 'Y':
                            success = self.launch_bot(self.bots[choice])
                            if success:
                                input("Press Enter to return to main menu...")
                            break
                        elif action == 'N':
                            break
                        elif action == 'I':
                            self.show_detailed_info(choice)
                        else:
                            self.log(f"{Fore.RED}Invalid option. Please choose Y, N, or I.{Style.RESET_ALL}")
                            await asyncio.sleep(1)
                
                elif choice.upper() == 'Q':
                    self.log(f"{Fore.YELLOW}Quick exit requested{Style.RESET_ALL}")
                    break
                
                else:
                    self.log(f"{Fore.RED}Invalid selection. Please choose 1-11 or 0 to exit.{Style.RESET_ALL}")
                    await asyncio.sleep(2)
                    
            except KeyboardInterrupt:
                self.log(f"{Fore.YELLOW}Interrupted by user. Exiting...{Style.RESET_ALL}")
                break
            except Exception as e:
                self.log(f"{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
                await asyncio.sleep(2)

    def show_detailed_info(self, bot_key):
        """Show detailed bot information"""
        bot = self.bots[bot_key]
        self.clear_terminal()
        
        print(f"\n{Fore.LIGHTGREEN_EX + Style.BRIGHT}{'═' * 80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN + Style.BRIGHT}    {bot['icon']} {bot['name'].upper()} - DETAILED INFORMATION{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX + Style.BRIGHT}{'═' * 80}{Style.RESET_ALL}")
        
        # Try to read bot file for additional info
        try:
            with open(bot['file'], 'r') as f:
                content = f.read()
                
            # Extract class name
            import re
            class_match = re.search(r'class\s+(\w+)', content)
            class_name = class_match.group(1) if class_match else "Unknown"
            
            # Count functions
            function_count = len(re.findall(r'def\s+\w+', content))
            
            # File size
            file_size = os.path.getsize(bot['file'])
            
            print(f"{Fore.CYAN}📄 File Information:")
            print(f"   • File: {bot['file']}")
            print(f"   • Size: {file_size:,} bytes")
            print(f"   • Main Class: {class_name}")
            print(f"   • Functions: {function_count}")
            print(f"\n{Fore.YELLOW}🔧 Description:")
            print(f"   • {bot['description']}")
            print(f"\n{Fore.GREEN}🚀 Status: {'Ready to Launch' if self.validate_bot_file(bot['file']) else 'File Missing'}")
            
        except Exception as e:
            print(f"{Fore.RED}Error reading bot file: {e}{Style.RESET_ALL}")
        
        print(f"\n{Fore.LIGHTGREEN_EX + Style.BRIGHT}{'═' * 80}{Style.RESET_ALL}")
        input("Press Enter to continue...")

    async def run(self):
        """Run the main menu"""
        await self.main()


if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # Initialize menu system
    menu = PharosMainMenu()
    
    try:
        asyncio.run(menu.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW + Style.BRIGHT}Menu interrupted by user. Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED + Style.BRIGHT}Fatal error: {str(e)}{Style.RESET_ALL}")
    finally:
        print(f"{Fore.CYAN + Style.BRIGHT}Thank you for using Pharos Bot Collection!{Style.RESET_ALL}")
