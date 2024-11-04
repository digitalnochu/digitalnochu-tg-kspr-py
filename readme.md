# Simple Telegram Commands for KSPR Bots
This Python project was developed as a conceptual idea to provide simplified control over KSPR Bots 1-10 through a command prompt interface on your PC. The application leverages the Bot API of Telegram to achieve this.

**Disclaimer**: it is essential to understand that this project is not 100% foolproof and may still contain unresolved issues or limitations. While efforts have been made to ensure functionality, users should exercise caution and be prepared for potential bugs or unanticipated behaviors. This application is intended for use as-is, with no guarantees of complete reliability.

- Idealized: _Oct 26, 2024_
- Developed: _Oct 27, 2024_
- First Official Run: _Oct 29, 2024_
- Number of official runs by dev as of Nov 4 2024: _5 runs_


## Installation
### Step 1: Python setup
1. Make sure Python is installed on your device https://www.python.org/downloads/
2. run cmd and prompt these two:
```bash
    pip install telethon
```
```bash
    pip install python-dotenv
```

### Step 2: Application setup
1. You need to register your phone, create an application and grab the APP ID and APP Hash from the official App of Telegram here: https://my.telegram.org/apps
2. Open the projects .env and enter your app details correctly.
```bash
user_NAME=username
user_API_ID=11111111
user_API_HASH=1234567890asdfghjkl
user_PHONE=+639111111111
user_BOTS=1-10
```

### Step 3: Run
1. run project by command prompt
```bash
    python pv6.py
```
or
```bash
    # run this if you want to command /mint in one-line. see Usage section below.
    python pv7.py 
```
or
```bash
    # run this if you want to command /mint in one-line + apply to all accounts asynchronously. see Usage section below.
    python pv8.py 
```

## Adding more accounts
Inside the pv6.py/pv7.py file, you will find the accounts variable holding an array of each account details.
```python
accounts = [
    { "name": os.getenv("user_NAME"), "api_id": os.getenv("user_API_ID"), "api_hash": os.getenv("user_API_HASH"), "phone": os.getenv("user_PHONE"), "bot_range": os.getenv("user_BOTS") }
]
```
as well as a line of code that says
```python
if account_choice not in ["username"]:
```
If you will add more accounts, be sure to update this *code block* and the *.env file*. Making sure both code blocks are one and same. Example below:

```python
# in .env file
user_NAME=username
user_API_ID=11111111
user_API_HASH=1234567890asdfghjkl
user_PHONE=+639111111111
user_BOTS=1-10

user2_NAME=username2
user2_API_ID=22222222
user2_API_HASH=1234567890asdfghjkl
user2_PHONE=+639222222222
user2_BOTS=1-10

# pv6.py / pv7.py line #22 / pv8.py line #23
accounts = [
    { "name": os.getenv("user_NAME"), "api_id": os.getenv("user_API_ID"), "api_hash": os.getenv("user_API_HASH"), "phone": os.getenv("user_PHONE"), "bot_range": os.getenv("user_BOTS") },
    { "name": os.getenv("user2_NAME"), "api_id": os.getenv("user2_API_ID"), "api_hash": os.getenv("user2_API_HASH"), "phone": os.getenv("user2_PHONE"), "bot_range": os.getenv("user2_BOTS") }
]

# pv6.py line 119 / pv7.py line 143 / pv8.py line 138
if account_choice not in ["username","username2"]:
```


## Usage

Command Syntax
```bash
<command> <optional: bot number or bot range>
```

Specific command Syntax of /mint when using pv7.py and pv8.py
```bash
/mint <ticker_name> <how_many_times_to_mint> <custom_gas_fee>

# example: /mint kaspy 100 1.7
# at the moment, you can't declare bot range in this syntax. So /mint command will default to use the bot range declared in .env file
```

## Main Commands
```python
/balance
/mint (+1 optional parameter)   # pv6.py
/mint (+3 parameters)           # pv7.py, pv8.py
/marketplace
/mylistings
```

## Other Commands
```python
exit                # exit python run
cancel              # can cancel everywhere. returns to "Enter command"
change account      # change active telegram user
change range	    # change active default bot numbers
bot range           # check active default bot numbers
```

## Attributes

**1. /balance _<any number or consecutive range>_**
```python	
        /balance            # runs on bot specified in .env file
        /balance 3          # only runs on bot 3
        /balance 5-10       # only runs on bot 5-10
```
**2. /mint _<any number or consecutive range>_**
```python				
        /balance            # runs on bot specified in .env file
        /mint 3             # only runs on bot 3
        /mint 5-10          # only runs on bot 5-10
```			
NOTE: 
    any succeeding commands after **/mint**, will only apply to bots you  have specified accordingly.

example	
```python	
    /mint           # runs on bots specified in .env file when you enter KRCtoken name, minting times, and gas fee
    /mint 3-5       # runs only on bots 3-5 when you enter KRCtoken name, minting times, and gas fee
```

## Limitations	
1. This is only limited to KSPR Bots 1-10 at the moment.
   
2. Try not to execute "other commands" inside /mint. or any other commands not related to /mint.		
**For example**, avoid running "change account" while inside "/mint" command. best to run "cancel" first before running other commands						
								
3. Ensure you are replying your answer to the correct question. Instructions per command are added to keep you in track. Replying incorrectly may cause potential errors.						
**Example** instruction includes "Enter command", "Which KRC20 Token...", "How many times..."						
								
3. Simultaneously monitor telegram updates vs. command prompt updates. To make sure you can resolve any issues that arises.	