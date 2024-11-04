import os
from dotenv import load_dotenv
import logging
import asyncio
from telethon import TelegramClient
from telethon.sync import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from datetime import datetime
from telethon import events
import time
import re

load_dotenv()

# Configure logging
logging.basicConfig(
    filename='bot_commands.log',  # Log file name
    level=logging.INFO,           # Log level (INFO level is suitable for general logging)
    format='[%(asctime)s] %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'   # Date and time format in log
)

accounts = [
    { "name": os.getenv("user_NAME"), "api_id": os.getenv("user_API_ID"), "api_hash": os.getenv("user_API_HASH"), "phone": os.getenv("user_PHONE"), "bot_range": os.getenv("user_BOTS") },
    { "name": os.getenv("user2_NAME"), "api_id": os.getenv("user2_API_ID"), "api_hash": os.getenv("user2_API_HASH"), "phone": os.getenv("user2_PHONE"), "bot_range": os.getenv("user2_BOTS") }
]

bot_range = "1-10"  # Initialize with a default value

def create_prompt(account_name):
    return f"{account_name} > " if account_name else "> "

async def process_account(account, command_base, command_args, effective_range):
    client = TelegramClient(f"session_{account['phone']}", account['api_id'], account['api_hash'])

    print(f"Connecting to {account['name']}...")
    await client.connect()

    if not await client.is_user_authorized():
        try:
            await client.send_code_request(account['phone'])
            code = input(f'Enter the code you received for {account["phone"]}: ')
            await client.sign_in(account['phone'], code)
        except SessionPasswordNeededError:
            password = input(f'Enter your password for {account["phone"]}: ')
            await client.sign_in(password=password)

    # Parse the bot range input to get the indices of bots to be processed
    bot_indices = parse_bot_range(effective_range)

    # Send the command to the specified bots
    if command_base == "/mint":
        command_parts = command_args.split(' ')

        for i in bot_indices:
            if 1 <= i <= 10:
                bot_username = f"@kspr_{i}_bot"
                await client.send_message(bot_username, command_base)
                logging.info(f"{command_base} command sent to {bot_username} from account {account['name']}.")

        for arg in command_parts:
            for i in bot_indices:
                if 1 <= i <= 10:
                    bot_username = f"@kspr_{i}_bot"
                    await client.send_message(bot_username, arg)
                    logging.info(f"{command_base} command sent to {bot_username} from account {account['name']}.")
    else:
        for i in bot_indices:
            if 1 <= i <= 10:
                bot_username = f"@kspr_{i}_bot"
                await client.send_message(bot_username, command_base)
                logging.info(f"{command_base} command sent to {bot_username} from account {account['name']}.")

    await client.disconnect()

    # Print completion message based on the command
    if command_base == '/balance':
        print(f"All balances refreshed for {account['name']} (Bots: {effective_range}).")
    elif command_base == '/mint':
        print(f"Mint command initiated for {account['name']} (Bots: {effective_range}).")
    elif command_base == '/send':
        print(f"Sending process initiated for {account['name']} (Bots: {effective_range}).")
    else:
        print("Command executed successfully.")

async def wait_for_response(client, bot_username):
    async for message in client.iter_messages(bot_username, limit=5):
        if message:
            print(f"Received message from {bot_username}")
            return  # Exit after receiving the first message
        
async def execute_command_for_accounts(account_choice, command_base, command_args, effective_range):
    try:
        if account_choice == "all":
            # Run process_account concurrently for each account in the list
            tasks = [process_account(account, command_base, command_args, effective_range) for account in accounts]
            await asyncio.gather(*tasks)
        else:
            selected_account = next(acc for acc in accounts if acc["name"].lower() == account_choice.lower())
            await process_account(selected_account, command_base, command_args, effective_range)
        return True
    except Exception as e:
        print(f"An error occurred while executing the command: {e}")
        return False

async def main():
    global bot_range  # Declare bot_range as global
    last_command = None  # Variable to keep track of the last command sent

    while True:
        print("\nEnter /start to start aranochu-py")
        start_command = input(create_prompt("")).strip().lower()

        command_status = check_user_command(start_command)
        if command_status == "exit":
            break  # Exit the main loop

        if command_status == "change_account":
            continue  # Go back to account selection

        if command_status == "change_range":
            continue  # Go back to command input after changing the range

        if command_status == "/start":
            while True:
                account_choice = None
                while True:
                    print("\nChoose account (username, username2 or all)")
                    account_choice = input(create_prompt("")).strip().lower()

                    command_status = check_user_command(account_choice)
                    if command_status == "exit":
                        return
                    
                    if command_status == "cancel":
                        continue  # Go back to account selection prompt
                        
                    if account_choice not in ["username", "username2", "all"]:
                        print("\nInvalid account choice. Please try again.")
                        continue
                    
                    # Handle "all" choice or get the selected account
                    if account_choice == "all":
                        bot_range = "1-10"  # Default bot range for "all" accounts
                        print("You have chosen all accounts. Bot range uses .env value")
                    else:
                        selected_account = next(acc for acc in accounts if acc["name"].lower() == account_choice)
                        bot_range = selected_account["bot_range"]
                        print(f"You have chosen {selected_account['name']}. Default bot range is {bot_range}.")
                    break

                while True:
                    print("\nEnter command")
                    user_command = input(create_prompt(account_choice)).strip().lower() 

                    command_status = check_user_command(user_command, account_choice)
                    if command_status == "exit":
                        return
                    if command_status == "change_account":
                        break  # Go back to account selection
                    if command_status in ["change_range", "bot_range", "cancel"]:
                        continue  # Go back to command input after changing the range

                    command_parts = user_command.split(' ')
                    command_base = command_parts[0]
                    specified_range = command_parts[1] if len(command_parts) > 1 else None

                    if specified_range and command_base != "/mint":
                        if specified_range.isdigit():
                            effective_range = specified_range
                        elif '-' in specified_range:
                            range_parts = specified_range.split('-')
                            if len(range_parts) == 2 and all(part.isdigit() for part in range_parts):
                                start, end = map(int, range_parts)
                                if start <= end:
                                    effective_range = f"{start}-{end}"
                                else:
                                    print("Invalid range: start must be less than or equal to end.")
                                    continue
                            else:
                                print("Invalid range format. Please use 'X' or 'X-Y'.")
                                continue
                        else:
                            print("Invalid input. Please enter a valid number or range.")
                            continue
                    else:
                        effective_range = bot_range

                    if command_base == "/mint":
                        token_to_mint = command_parts[1] if len(command_parts) > 1 else None
                        times_to_mint = int(command_parts[2]) if len(command_parts) > 2 else None
                        amt_mint = float(command_parts[3]) if len(command_parts) > 3 else None

                        if not token_to_mint or not times_to_mint or not amt_mint:
                            print("\nInvalid /mint command. Please provide all required arguments (e.g., /mint token_name 100 1.6).")
                            continue

                        await execute_command_for_accounts(account_choice, command_base, f"{token_to_mint} {times_to_mint} {amt_mint}", effective_range)
                        print(f"\nMinting {times_to_mint} times for {token_to_mint} with {amt_mint} gas. Check Telegram for updates.")
                        last_command = user_command
                    elif command_base in ["/balance", "/send", "/marketplace", "/mylistings"]:
                        await execute_command_for_accounts(account_choice, user_command, [], effective_range)
                        last_command = user_command
                    else:
                        print("\nInvalid command. Please try again.")
        


def check_user_command(command, account_name=None):
    global bot_range  # Declare bot_range as global at the beginning of the function
    if command == "exit":
        print("Exiting...\n")
        return "exit"  # Return a special command for exiting
    
    if command == "change account":
        return "change_account"  # Return a special command for changing account
    
    if command == "cancel":
        return "cancel"
    
    if command == "bot range":
        print(f"\nYour current range of bots is {bot_range}.")
        return "bot_range"
    
    if command == "change range":
        print(f"\nYour current range of bots is {bot_range}. \nEnter new range of bots to execute (e.g., '1-5', '1-3, 8-9', '1-10')")
        new_range = input().strip().lower()
        bot_range = new_range  # Update the global bot_range

        # Save the new bot range to the .env file for the specific account
        if account_name:
            # Determine the environment variable to update
            env_var_name = f"{account_name.lower()}_BOTS"
            
            # Read the existing .env file
            try:
                with open('.env', 'r') as file:
                    lines = file.readlines()

                # Write back to .env, updating the specific bot range line
                with open('.env', 'w') as file:
                    for line in lines:
                        if line.startswith(env_var_name + "="):  # Check for the specific bot range
                            file.write(f"{env_var_name}={bot_range}\n")  # Update the line
                        else:
                            file.write(line)  # Write the line back unchanged
                print(f"Updated {env_var_name} in .env file to: {bot_range}")

            except Exception as e:
                # Debugging: handle exceptions and print errors
                print(f"Error updating .env file: {e}")
            
        return "change_range"  # Return a special command for changing range
    
    else:
        return command  # Return the original command

def parse_bot_range(input_range):
    # Parse input ranges (e.g., "1-5", "1-10", "1-3, 8-9") and return a list of bot indices
    indices = set()
    parts = input_range.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            start, end = int(start), int(end)
            indices.update(range(start, end + 1))
        else:
            indices.add(int(part))
    return sorted(indices)

# Run the script
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())