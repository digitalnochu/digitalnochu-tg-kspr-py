import os
from dotenv import load_dotenv
import logging
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

# Replace these with your own values for each account
accounts = [
    { "name": os.getenv("user_NAME"), "api_id": os.getenv("user_API_ID"), "api_hash": os.getenv("user_API_HASH"), "phone": os.getenv("user_PHONE"), "bot_range": os.getenv("user_BOTS") },
    { "name": os.getenv("user2_NAME"), "api_id": os.getenv("user2_API_ID"), "api_hash": os.getenv("user2_API_HASH"), "phone": os.getenv("user2_PHONE"), "bot_range": os.getenv("user2_BOTS") }
]

bot_range = "1-10"  # Initialize with a default value

def create_prompt(account_name):
    return f"{account_name} > " if account_name else "> "

async def process_account(account, command, effective_range):
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
    for i in bot_indices:
        if 1 <= i <= 10:  # Ensure the bot index is within the valid range
            bot_username = f"@kspr_{i}_bot"

            # Send the command to each bot
            await client.send_message(bot_username, command)

            # Log the command sent
            log_message = f"{command} command sent to {bot_username} from account {account['name']}."
            logging.info(log_message)

    await client.disconnect()

    # Print completion message based on the command
    if command == '/balance':
        print(f"All balances refreshed for {account['name']} (Bots: {effective_range}).")
    elif command == '/mint':
        print(f"Mint command initiated for {account['name']} (Bots: {effective_range}).")
    elif command == '/send':
        print(f"Sending process initiated for {account['name']} (Bots: {effective_range}).")
    else:
        print("Command executed successfully.")

async def execute_command_for_accounts(account_choice, command, effective_range):
    try:
        if account_choice == "all":
            for account in accounts:
                await process_account(account, command, effective_range)
        else:
            selected_account = next(acc for acc in accounts if acc["name"] == account_choice)
            await process_account(selected_account, command, effective_range)
        return True  # Return True on successful execution
    except Exception as e:
        print(f"An error occurred while executing the command: {e}")
        return False  # Return False in case of an error

async def main():
    global bot_range  # Declare bot_range as global
    last_command = None  # Variable to keep track of the last command sent

    while True:
        print("\nEnter /start to start aranochu-py")
        start_command = input(create_prompt("")).strip().lower()  # Arrow for input prompt

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
                    print("\nChoose account:")
                    account_choice = input(create_prompt("")).strip().lower()  # Arrow for input prompt

                    command_status = check_user_command(account_choice)
                    if command_status == "exit":
                        return
                    
                    if command_status == "cancel":
                        continue  # Go back to account selection prompt
                        
                    if account_choice not in ["username","username2"]:
                        print("\nInvalid account choice. Please try again.")
                        continue
                    
                    # Get and display the default bot range for the selected account
                    selected_account = next(acc for acc in accounts if acc["name"].lower() == account_choice)
                    bot_range = selected_account["bot_range"]
                    print(f"You have chosen {selected_account['name']}. Default bot range is {bot_range}.")
                    break

                while True:
                    print("\nEnter command")
                    user_command = input(create_prompt(account_choice)).strip().lower() 

                    command_status = check_user_command(user_command, account_choice)  # Pass account_choice here
                    if command_status == "exit":
                        return
                    if command_status == "change_account":
                        break  # Go back to account selection
                    if command_status in ["change_range", "bot_range", "cancel"]:
                        continue  # Go back to command input after changing the range

                    # Determine the range to use
                    command_parts = user_command.split(' ')
                    command_base = command_parts[0]  # The command (e.g., /mint, /balance)
                    specified_range = command_parts[1] if len(command_parts) > 1 else None  # Check for a specified range

                    # Validate and process the specified range
                    if specified_range:
                        # Check for single number (e.g., "3") or range (e.g., "6-10")
                        if specified_range.isdigit():  # Single number
                            effective_range = specified_range
                        elif '-' in specified_range:  # Range
                            range_parts = specified_range.split('-')
                            if len(range_parts) == 2 and all(part.isdigit() for part in range_parts):
                                start, end = map(int, range_parts)
                                if start <= end:  # Ensure the start is less than or equal to end
                                    effective_range = f"{start}-{end}"
                                else:
                                    print("Invalid range: start must be less than or equal to end.")
                                    continue  # Skip further processing
                            else:
                                print("Invalid range format. Please use 'X' or 'X-Y'.")
                                continue  # Skip further processing
                        else:
                            print("Invalid input. Please enter a valid number or range.")
                            continue  # Skip further processing
                    else:
                        effective_range = bot_range  # Fall back to the default bot range

                    if command_base == "/mint":
                        # Send the /mint command to process_account first
                        await execute_command_for_accounts(account_choice, user_command, effective_range)  # Pass the effective range
                        last_command = user_command  # Store the last command
                        cancel_triggered = False

                        while True:
                            if cancel_triggered:
                                cancel_triggered = False 
                                continue

                            print("\nWhich KRC20 token do you want to mint?")
                            token_to_mint = input(create_prompt(account_choice)).strip().lower()  # Arrow for input prompt

                            command_status = check_user_command(token_to_mint, account_choice)  # Pass account_choice here

                            if command_status == "exit":
                                return
                            if command_status == "change_account":
                                break  # Go back to account selection
                            if command_status in ["change_range", "bot_range"]:
                                continue  # Go back to command input after changing the range
                            if command_status == "cancel":
                                # Send a /balance command to clear the /mint request
                                await execute_command_for_accounts(account_choice, "/balance", effective_range)
                                cancel_triggered = True
                                break  # Redirect all the way back to the main command entry point

                            if token_to_mint == "/mint":
                                # If the user inputs "/mint", notify and re-prompt
                                print("\nYou have already entered /mint command.")
                                continue  # Re-prompt for the KRC20 token

                            if not token_to_mint:
                                print("\nNo token entered. Please try again.")
                                continue  # Re-prompt for the KRC20 token

                            mint_command = f"{token_to_mint}"

                            # Send the KRC20 token mint command to process_account with the effective range
                            success = await execute_command_for_accounts(account_choice, mint_command, effective_range)

                            if success:

                                times_to_mint = 0 
                                amt_mint = 0.0

                                while True:
                                    try:
                                        # HOW MANY TIMES TO MINT? 
                                        print("\nHow many times would you like to mint?")
                                        times_to_mint_input = input(create_prompt(account_choice)).strip().lower()

                                        command_status = check_user_command(times_to_mint_input, account_choice)  # Check for "cancel"
                                        if command_status in ["exit", "change_account", "cancel"]:
                                            await execute_command_for_accounts(account_choice, "/balance", effective_range)
                                            if command_status == "cancel":
                                                cancel_triggered = True
                                            break  # Redirect all the way back to the main command entry point

                                        times_to_mint = int(times_to_mint_input)
                                        
                                        if times_to_mint <= 0:
                                            print("Please enter a positive integer.")
                                            continue
                                        break
                                    except ValueError:
                                        print("Invalid input. Please enter a number.")

                                if cancel_triggered:
                                    break

                                mint_count_command = f"{times_to_mint}"
                                success = await execute_command_for_accounts(account_choice, mint_count_command, effective_range)

                                if success:
                                    # AMOUNT TO MINT?
                                    print(f"\nMinting {times_to_mint} times for {token_to_mint}. Check Telegram for updates.")

                                    while True:
                                        try:
                                            # ENTER CUSTOM GAS AMOUNT
                                            print("\nEnter Custom Gas Amount")
                                            amt_mint_input = input(create_prompt(account_choice)).strip().lower()

                                            command_status = check_user_command(amt_mint_input, account_choice)  # Check for "cancel"
                                            if command_status in ["exit", "change_account", "cancel"]:
                                                await execute_command_for_accounts(account_choice, "/balance", effective_range)
                                                if command_status == "cancel":
                                                    cancel_triggered = True
                                                break  # Redirect all the way back to the main command entry point

                                            amt_mint = float(amt_mint_input)
                                            
                                            if amt_mint <= 0:
                                                print("Please enter a positive integer.")
                                                continue
                                            break
                                        except ValueError:
                                            print("Invalid input. Please enter a number.")

                                    if cancel_triggered:
                                        break  # Redirect all the way back to the main command entry point

                                    mint_amt_command = f"{amt_mint}"
                                    success = await execute_command_for_accounts(account_choice, mint_amt_command, effective_range)

                                    if success:
                                        print("Done..")
                                        break
                                    else:
                                        print("\nFailed to execute mint command. Please try again.")

                                else:
                                    print("\nFailed to execute mint command. Please try again.")
                            else:
                                print("\nFailed to execute mint command. Please try again.")


                    elif command_base in ["/balance", "/send", "/marketplace" ,"/mylistings"]:
                        await execute_command_for_accounts(account_choice, user_command, effective_range)
                        last_command = user_command  # Store the last command
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