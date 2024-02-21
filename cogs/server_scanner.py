from discord.ext import commands
from server_data import ServerData
from bot_state import BotState
import asyncio
import settings


from utils import validate_server_number


class ServerScanner(commands.Cog):

    def __init__(self, bot, bot_state: BotState):
        self.bot = bot
        self.server_data = ServerData()
        self.bot_state = bot_state

        # Key: discord server id, Value: list of Ark server numbers
        self.running_status_in_servers = {}
        self.running_autpop_in_servers = set()

    @commands.command()
    async def pop(self, ctx, server_number: int):

        if not await validate_server_number(ctx, server_number):
            return

        pop_msg = self.server_data.pop(server_number)

        await ctx.send(embed=pop_msg)

    @commands.command()
    async def status(self, ctx, server_number: int):

        if not await validate_server_number(ctx, server_number):
            return

        server_id = ctx.guild.id
        if server_number in self.running_status_in_servers.get(server_id):
            await ctx.send(f"I'm already looking for {server_number} status, wait :rage: ")
            return

        if server_id not in self.running_status_in_servers:
            self.running_status_in_servers[server_id] = [server_number]
        else:
            self.running_status_in_servers[server_id].append(server_number)

        role = f"<@&492494724528340992>"  # @Member role

        await ctx.send(f"Cheching {server_number} status...")

        self.bot_state.state["status"] = True

        counter = 0
        while self.bot_state.get("status"):

            if not self.server_data.is_server_down(server_number):
                await ctx.send(f"{role} {server_number} is up!")
                print(f"{server_number} status: Online")
                self.bot_state.state["status"] = False
                break

            # Server is still down
            counter += 1
            print(f"{server_number} status: Down - {counter}")
            await asyncio.sleep(settings.status_interval)

        self.running_status_in_servers[server_id].remove(server_number)
