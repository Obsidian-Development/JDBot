import discord, random
import utils
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.menus.views import ViewMenuPages
    
class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def cog_command_error(self, ctx, error):
    if ctx.command or not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()

  @commands.cooldown(1, 20, BucketType.user)
  @commands.command(brief = "you can pick a job and then work it in this work command")
  async def work(self, ctx):

    member = ctx.author
    add_money = 10

    await self.bot.db2.execute("UPDATE economy SET wallet = wallet + ($1) WHERE user_id = ($2)", add_money, member.id)

    await ctx.send(f"You worked the basic job and got ${add_money}. (more jobs coming soon)")

  @commands.cooldown(1, 15, BucketType.user)
  @commands.command(brief = "a command to send how much money you have", help = "using the JDBot database you can see how much money you have", aliases = ["bal"])
  async def balance(self, ctx, *, member: utils.BetterMemberConverter = None):

    member = member or ctx.author

    economy = await self.bot.db2.fetchrow("SELECT * FROM economy WHERE user_id = ($1)", member.id)

    if not economy:
      view = utils.BasicButtons(ctx)

      if ctx.author.id != member.id:
        return await ctx.send(f"You aren't {member}. \nOnly they can join the database. You must ask them to join if you want them to be in there")

      msg = await ctx.send(f"{member}, needs to join the database to run this. You can do it now", view = view)

      await view.wait()
      
      if view.value is None:
        return await msg.edit("you didn't respond quickly enough")

      if not view.value:
        return await msg.edit("Not adding you to the database")

      if view.value:
        await ctx.send("adding you to the database for economy...")

        await self.bot.db2.execute("INSERT INTO economy(user_id) VALUES ($1)", member.id)

        economy = await self.bot.db2.fetchrow("SELECT * FROM economy WHERE user_id = ($1)", (member.id,))

    wallet = economy.get("wallet")
    bank = economy.get("bank")

    embed = discord.Embed(title = f"{member}'s Balance:", color = random.randint(0, 16777215))
    embed.add_field(name = "Wallet:", value = f"${wallet}")
    embed.add_field(name = "Bank:", value = f"${bank}")
    embed.add_field(name = "Total:", value = f"${wallet+bank}")
    embed.add_field(name = "Currency:", value = "<:JDJGBucks:779516001782988810>")
    embed.set_footer(text = "Do not for any reason, trade JDJGbucks, sell or otherwise use real money or any other money to give others JDJGBucks or receive.")
    await ctx.send(embed = embed)
  
  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief = "a leaderboard command goes from highest to lowest", aliases = ["lb"])
  async def leaderboard(self, ctx):
    
    data = await self.bot.db2.fetch("SELECT * FROM economy ORDER BY wallet + BANK DESC")

    ndata = []
    for n in data:
      place = [n[0] for n in data].index(n[0])
      user = await self.bot.try_user(n[0])

      ndata.append([f"{place + 1}. {user}", n[1], n[2]])
    
    ndata = utils.groupby(ndata, 6)

    menu = ViewMenuPages(utils.LeaderboardEmbed(ndata, per_page = 1), delete_message_after = True)
  
    await menu.start(ctx)


def setup(bot):
  bot.add_cog(Economy(bot))