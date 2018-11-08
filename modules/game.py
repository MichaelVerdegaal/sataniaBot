import asyncio
import random

import discord
from discord.ext import commands

from util.game_util import *
from db_connection import *
from models.users import User
from sqlalchemy import func


class Game:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['g'], hidden=True)
    @commands.is_owner()
    async def grant(self, ctx, score):
        """|Gives an user points"""
        user = ctx.message.mentions[0]
        author = user.id
        if not user.bot:
            increment_score(author, score)
            await ctx.send(f"User {user} has been given **{score}** points.")
            await asyncio.sleep(const.DELETE_TIME)
            await ctx.message.delete()

    @commands.command(aliases=['p'])
    async def profile(self, ctx):
        """|Check how high your IQ is"""
        user = user_get(ctx.message.author.id)
        embed = discord.Embed(title=f"Profile for {user.dname}",
                              description="Your stats for Satania\'s wonderful games",
                              color=0xe41b71)
        embed.add_field(name="IQ", value=user.score, inline=True)
        embed.add_field(name="Reactions triggered", value=user.reactions_triggered, inline=True)
        await ctx.send(embed=embed)
        await asyncio.sleep(const.DELETE_TIME)
        await ctx.message.delete()

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, page_count=1):
        """|Shows the leaderboard for the IQ games"""
        page_constant = 12
        low_bound = (page_count - 1) * page_constant + 1
        high_bound = page_constant * page_count

        row_number = func.row_number().over(order_by=(User.score.desc(), User.dname)).label('row_number')
        query = session.query(User)
        query = query.add_column(row_number)
        query = query.from_self().filter(row_number.between(low_bound, high_bound))

        rows = query.all()
        embed = discord.Embed(title="Leaderboard")
        for row in rows:
            user = row[0]
            ranking = row[1]
            embed.add_field(name=f"#{ranking} {user.dname[:20]}",
                            value=f"IQ: {user.score}", inline=True)
        embed.set_footer(text=f"Page {page_count}")
        await ctx.send(embed=embed)
        await asyncio.sleep(const.DELETE_TIME)
        await ctx.message.delete()

    @commands.command()
    async def flip(self, ctx, bet, guess):
        """|Flip a coin"""
        bet = int(bet)
        flip_arguments = ['h', 't']
        result = random.choice(flip_arguments)
        flip_full = ''
        flip_image = ''
        author = ctx.message.author.id
        balance = user_get(author).score

        if balance < bet:
            await ctx.send("You don't have enough points for that.")
        else:
            if result is 'h':
                flip_full = 'heads'
                flip_image = const.FLIP_IMAGE_HEADS
            elif result is 't':
                flip_full = 'tails'
                flip_image = const.FLIP_IMAGE_TAILS
            if guess in flip_arguments:
                if bet >= 10:
                    embed = discord.Embed(title=f"{ctx.message.author.name} flipped {flip_full}",
                                          color=0xe41b71)
                    embed.set_image(url=flip_image)
                    if guess is result:
                        won_points = round((bet * 1.5) - bet)
                        embed.description = f"You gain {won_points} IQ points!"
                        increment_score(author, won_points)
                    elif guess is not result:
                        embed.description = "You lost."
                        reduce_score(author, bet)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('Please enter a bet of at least 10.')
            else:
                await ctx.send('Please send a valid command')

    @commands.command()
    async def roll(self, ctx, bet):
        """|Roll the dice"""
        bet = int(bet)
        author = ctx.message.author.id
        balance = user_get(author).score
        r_number = int(random.uniform(1, 101))
        won_points = 0
        multipliers = [0, 0.8, 1.2, 1.5, 1.7]

        if balance < bet:
            await ctx.send("You don't have enough points for that.")
        else:
            if bet >= 10:
                embed = discord.Embed(title=f"You rolled a {r_number}", color=0xe41b71)
                if r_number <= 20:
                    won_points = round((bet * multipliers[0]))
                elif r_number <= 50:
                    won_points = round((bet * multipliers[1]))
                elif r_number <= 70:
                    won_points = round((bet * multipliers[2]) - bet)
                elif r_number <= 90:
                    won_points = round((bet * multipliers[3]) - bet)
                elif r_number <= 100:
                    won_points = round((bet * multipliers[4]) - bet)

                if won_points < bet:
                    embed.description = f"You lost {won_points} points."
                    reduce_score(author, won_points)
                else:
                    embed.description = f"You won {won_points} points!"
                    increment_score(author, won_points)
                await ctx.send(embed=embed)
            else:
                await ctx.send('Please enter a bet of at least 10')


def setup(bot):
    bot.add_cog(Game(bot))
