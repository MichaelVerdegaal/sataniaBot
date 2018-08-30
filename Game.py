import time
import discord
import random

from discord.ext import commands
from dbconn import *

DELETE_TIME = 15


class GameUtils:

    def user_exists(self):
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE did = %s ", (self,))
        row = cur.fetchone()
        cur.close()
        if row:
            return True
        else:
            return False

    def user_get(self):
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE did = %s ", (self,))
        row = cur.fetchone()
        cur.close()
        return row

    def user_create(self, discord_name, score=0, reactions_triggered=0):
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (self, discord_name, score, reactions_triggered))
        print("Posted user to DB | {}: {}".format(self, discord_name))
        cur.close()

    def increment_score(self, score):
        cur = conn.cursor()
        cur.execute("UPDATE users SET score = score + %s WHERE did = %s", (score, self))
        cur.close()

    def reduce_score(self, score):
        cur = conn.cursor()
        cur.execute("UPDATE users SET score = score - %s WHERE did = %s", (score, self))
        cur.close()

    def multiply_score(self, score):
        cur = conn.cursor()
        cur.execute("UPDATE users SET score = score * %s WHERE did = %s", (score, self))
        cur.close()

    def increment_rcounter(self, score):
        cur = conn.cursor()
        cur.execute("UPDATE users SET reactions_triggered = reactions_triggered + %s WHERE did = %s", (score, self))
        cur.close()


class Game:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['g'], hidden=True)
    @commands.is_owner()
    async def grant(self, ctx, score, mention):
        """|Gives an user points"""
        user = ctx.message.mentions[0]
        if not user.bot:
            GameUtils.increment_score(user.id, score)
            await ctx.send("User {} has been given **{}** points.".format(user, score))
            time.sleep(DELETE_TIME)
            await ctx.message.delete()

    @commands.command(aliases=['p'])
    async def profile(self, ctx):
        """|Check how high your IQ is"""
        did = ctx.message.author.id
        user = GameUtils.user_get(did)
        embed = discord.Embed(title="Profile for {}".format(user[1]),
                              description="Look at your stats for Satania\'s IQ games", color=0xe41b71)
        embed.add_field(name="IQ", value=user[2], inline=True)
        embed.add_field(name="Reactions triggered", value=user[3], inline=True)
        await ctx.send(embed=embed)
        time.sleep(DELETE_TIME)
        await ctx.message.delete()

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, page_count=1):
        """|Shows the leaderboard for the IQ games"""
        page_constant = 15
        low_bound = (page_count - 1) * page_constant + 1
        high_bound = page_constant * page_count
        sql = "SELECT  * " \
              "FROM (SELECT  *, ROW_NUMBER() OVER " \
              "(ORDER BY score DESC, dname ASC ) AS rn FROM users) q " \
              "WHERE rn BETWEEN %s and %s"
        cur = conn.cursor()
        cur.execute(sql, (low_bound, high_bound))
        rows = cur.fetchall()
        cur.close()
        response = ""
        for row in rows:
            if row[4] < 10:
                response += "#{}  IQ: {} | Reactions: {} | {}\n".format(row[4], row[2], row[3], row[1][:30])
            else:
                response += "#{} IQ: {} | Reactions: {} | {}\n".format(row[4], row[2], row[3], row[1][:30])
        await ctx.send("```{}\n\n   Page {}```".format(response, page_count))
        time.sleep(DELETE_TIME)
        await ctx.message.delete()

    @commands.command()
    async def flip(self, ctx, bet, guess):
        """|Flip a coin"""
        flip_arguments = ['h', 't']
        result = random.choice(flip_arguments)
        flip_full = ''
        flip_image = ''
        bet = int(bet)
        author = ctx.message.author.id
        balance = GameUtils.user_get(author)[2]

        if balance < bet:
            await ctx.send("You don't have enough points for that.")
        else:
            if result is 'h':
                flip_full = 'heads'
                flip_image = 'https://cdn.discordapp.com/attachments/386624118495248385/484690453594374156/sataniahead.png'
            elif result is 't':
                flip_full = 'tails'
                flip_image = 'https://cdn.discordapp.com/attachments/386624118495248385/484690459944550410/sataniatail.png'
            if guess in flip_arguments:
                if bet >= 10:
                    if guess is result:
                        won_points = round((bet * 1.5) - bet)
                        embed = discord.Embed(title="You flipped {}".format(flip_full),
                                              description="You gain {} IQ points!".format(won_points), color=0xe41b71)
                        embed.set_image(url=flip_image)
                        GameUtils.increment_score(author, won_points)
                    elif guess is not result:
                        embed = discord.Embed(title="{} flipped {}".format(ctx.message.author, flip_full),
                                              description="You lost.", color=0xe41b71)
                        GameUtils.reduce_score(author, bet)
                        embed.set_image(url=flip_image)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('Please enter a bet of at least 10.')
            else:
                await ctx.send('Please send a valid command')


def setup(bot):
    bot.add_cog(Game(bot))