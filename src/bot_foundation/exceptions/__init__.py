from discord.ext import commands


class UserBlackListed(commands.CheckFailure):
    """
    Get's thrown when someone tries to use a bot command but is found in the blacklist.'
    """
    def __init__(self, message="User is blacklisted."):
        self.message = message
        super().__init__(self.message)
        
        
class UserNotOwner(commands.CheckFailure):
    def __init__(self, message="User is not owner of the bot."):
        self.message = message
        super().__init__(self.message)
