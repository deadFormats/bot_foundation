import asyncio
import json
import logging
import os
import platform
import random
import sys

import discord
from discord.ext import commands,tasks
from discord.ext.commands import Bot, Context
from InquirerPy import inquirer
from InquirerPy.utils import patched_print
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from bot_foundation import exceptions
from bot_foundation.helpers import prompts


BASEDIR = os.path.abspath(os.path.dirname(__file__))
EMB_COLORS = {
    'red': 0xE02B2B,
}


if not os.path.isfile(os.path.join(BASEDIR, "config.json")):
    patched_print(f"There's no configuration file for the bot.")
    config_decision = inquirer.select(
        message="Cannot run without good configuration file, how do you want to proceed? >>> ",
        choices=[
            Choice(name="Interactive Config Setup", value="new_config"),
            Choice(name="Manually specify path to .cfg file.", value="find_via_path"),
            Separator(),
            Choice(name="Exit", value=False)
        ],
    ).execute()
    
    if not config_decision:
        sys.exit("Quitting...")
    elif config_decision == "new_config":
        config = prompts.new_config()
        
    elif config_decision == "find_via_path":
        file_path = prompts.prompt_for_filepath()
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                config = json.load(file)
                

# BOT SETUP HERE
bot = Bot(
    command_prefix=commands.when_mentioned_or(config['prefix']),
    intents=intents,
    help_command=None
)


# LOGGER SETUP HERE
class LoggingFormatter(logging.Formatter):
    # colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    #stles
    reset = "\x1b[0m"
    bold = "\x1b[1m"
    
    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold
    }
    
    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, '%Y-%m-%d %H:%M:%S', style="{")
        return formatter.format(record)
        
        
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)


# Console output handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())

# Log File Handler
file_handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}",
    '%Y-%m-%d %H:%M:%S',
    style="{"
)
file_handler.setFormatter(file_handler_formatter)


# Add all logging handlers 
logger.addHandler(console_handler)
logger.addHandler(file_handler)
bot.logger = logger


async def init_db():
    pass  # TODO
    
    
bot.config = config



# Bot events will be defined here (not commands)
@bot.event
async def on_ready() -> None:
    """
    This code will be executed once the bot is finished setting itself up
    """
    bot.logger.info(f"Logged in as {bot.user.name}")
    bot.logger.info(f"discord.py API version: {discord.__version__}")
    bot.logger.info(f"Python version: {platform.python_version()}")
    bot.logger.info(
        f"Running on: {platform.system()} {platform.release()} ({os.name})"
    )
    bot.logger.info("---------------------------------")
    status_task.start()
    if config['sync_commands_globally']:
        bot.logger.info("Performing a global sync on commands..")
        await bot.tree.sync()
        
        
"""
    Ideally, any background tasks that the bot is expected to perform should probably live within
    this section, unlerss there's no other way to implement the feature
"""
@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Simplified demonstration of background tasks using the bot's ability to change presences'
    """
    statuses = [
        "In a bot lobby",
        "Blowing all my money on crack",
        "My Taxes"
    ]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))
    
    
@bot.event 
async def on_message(message: discord.Message) -> None:
    """
    This is executed everytime a message is sent by ANYONE in the server. Currently, it actually
    serves no purpose and the bot would function without it being defined. However, if in the future 
    I implement functions that work off the 'on_message' event, this function will already contain the necessary 
    command processing bit so that way the functionality wouldn't interfere with normal use of commands'
    
    :param message: The message that was sent.
    """
    if message.author == bot.user or message.author.bot:
        return 
    await bot.process_commands(message)
    
    
@bot.event 
async def on_command_completion(context: Context) -> None:
    """
    This will execute whenever a command *successfully* executes.
    Purpose here is for logging really, but further functionality can be implemented.
    
    :param context: The command context
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    exec_command = str(split[0])
    if context.guild is not None:
        bot.logger.info(
            f"Executed {exec_command} in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
        )
    else:
        bot.logger.info(
            f"Executed {exec_command} by {context.author} (ID: {context.author.id})"
        )
        

@bot.event 
async def on_command_error(context: Context, error) -> None:
    """
    This will execute whenever a valid command throws some error, can be used to not only
    invoke the loggers but also to respond to the user with more details on the error.
    
    :param context: The command context
    :param error: The exception that was thrown 
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        
        embed = discord.Embed(
            description=f"**Please slow down** - Command available again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}",
            color=EMB_COLORS['red']
        )
        await context.send(embed=embed)
        
    elif isinstance(error, exceptions.UserBlackListed):
        """
        This error will be thrown anytime the user not blacklisted check fails
        """
        embed = discord.Embed(
            description="You are blacklisted from using the bot.",
            color=EMB_COLORS['red']
        )
        await context.send(embed=embed)
        bot.logger.warning(
            f"{context.author} (ID: {context.author.id}) tried to execute a command in guild {context.guild.name} (ID: {context.guild.id}), but the user is blacklisted."
        )
    
    elif isinstance(error, exceptions.UserNotOwner):
        embed = discord.Embed(
            description="You are not the owner of the bot.",
            color=EMB_COLORS['red']
        )
        await context.send(embed=embed)
        bot.logger.warning(
            f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id})"
        )
    
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description=f"You are missing the permission(s) `{', '.join(error.missing_permissions)}` to execute this command.",
            color=EMB_COLORS['red']
        )
    
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            description=f"I am missing the permission(s) `{', '.join(error.missing_permissions)}` to fully perform this command..",
            color=EMB_COLORS['red']
        )
        await context.send(embed=embed)
        
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            description=str(error).capitalize(),
            color=EMB_COLORS['red']
        )
        await context.send(embed=embed)
    else:
        raise error
        
        
        
#COG related stuff
async def load_cogs() -> None:
    """
    This will execute with every startup of the bot.
    """
    for file in os.listdir(os.path.join(os.path.realpath(os.path.dirname(__file__)), "cogs")):
        if file.endswith('.py'):
            extension = fild[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                bot.logger.info(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                bot.logger.error(f"Failed to load extension '{extension}'\n{exception}")
                
                
                
                
if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(load_cogs())
    bot.run(config['token'])
    
    
