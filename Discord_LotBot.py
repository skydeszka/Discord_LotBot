import os
import discord
from discord.ext import commands, tasks
from itertools import cycle
import random

bot = commands.Bot(command_prefix='!lotbot ')
statusJelOn = cycle(['!lotbot parancsok', 'Jelentkezések be!'])
statusJelOff = cycle(['!lotbot parancsok', 'Jelentkezések ki!'])
bot.jelentkezok = []
bot.nyertesek = []
bot.isItOn = False


def isBotOn(ctx):
	if bot.isItOn:
		return True
	else:
		return False


@bot.event
async def on_ready():
	change_status.start()
	print("Bot elindítva...")


@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.author.send(
		    'Psszt! Nem rendelkezel felhatalmazással a parancs használatára.')
	if isinstance(error, commands.errors.CommandNotFound):
		await ctx.send(f'{ctx.author.mention} nem létezik ilyen parancs.')


@tasks.loop(seconds=5)
async def change_status():
	if bot.isItOn == True:
		await bot.change_presence(activity=discord.Game(next(statusJelOn)))
	else:
		await bot.change_presence(activity=discord.Game(next(statusJelOff)))


#FELHASZNÁLÓ PARANCSOK


#KILEP
@bot.command(aliases=["kilép"])
async def kilep(ctx):
	isnotJoined = True
	for i in bot.jelentkezok:
		if i.__contains__(ctx.author.mention):
			del bot.jelentkezok[bot.jelentkezok.index(i)]
			isnotJoined = False
			await ctx.send(f'{ctx.author.mention} kiléptél a sorsolásból.')
	if isnotJoined:
		await ctx.send(f'{ctx.author.mention} még nem jelentkeztél sorsolásra.'
		               )


#PARANCSOK
@bot.command()
async def parancsok(ctx):
	await ctx.author.send(
	    "Parancsok:\n```!lotbot jelentkez - <Epic games név> <XBOX Gamertag vagy PSN ID> - Csak akkor töltsd ki az utolsó részt, ha konzolon játszol.``````!lotbot kilep - Kilépsz a sorsolásból(hasznosharosszul írod a neved)```\nNe felejtsd! Ha egyszer ki lettél sorsolva újra jelentkezned kell.\nPélda nevek:```PC:\nEpic név: \"lakatosbéla\"\n!lotbot jelentkez lakatosbéla``````Konzol:\nEpic név: \"lakatosbéla\"\nKonzol név:\"konzolosvagyok\"\n!lotbot jelentkez lakatosbéla konzolosvagyok```\n\n\nHA A NEVEDBEN SZÓKÖZ SZEREPEL EZT ÍRD A SZÓKÖZ HELYÉRE <space>\nPéldául:```Epic név: \"lakatos béla\"\n!lotbot lakatos<space>béla```\n\n```diff\n-FIGYELJETEK A NEVEKRE. HA ROSSZ NÉVVEL JELENTKEZEL ÉS NYERSZ, ÚJ NYERTEST SORSOLUNK!```"
	)


#JELENTKEZ
@bot.command(aliases=["join", "jelentkezz", "jelentkezem", "jelentkezek"])
@commands.check(isBotOn)
async def jelentkez(ctx, nev, psnev=""):
	user = ctx.author.mention
	nevteszt = 'Epic:\"' + nev + '\"'
	psnevteszt = 'Konzol:\"' + psnev + '\"'
	if (user not in str(bot.nyertesek)):
		if (user not in str(bot.jelentkezok)):
			if (nevteszt not in str(bot.jelentkezok)):
				if (psnevteszt not in str(bot.jelentkezok) or psnev == ""):
					nev = nev.replace('<space>', ' ')
					psnev = psnev.replace('<space>', ' ')
					if len(psnev) == 0:
						bot.jelentkezok.append(f'{user} - Epic:\"{nev}\"')
						print(
						    f'PC - Sorsolásra jelentkezett: {ctx.author}. Epic név: \"{nev}\"'
						)
						await ctx.send(
						    f'Sorsolásra feliratkozott: {user}, a következő névvel: \"{nev}\"'
						)
					else:
						bot.jelentkezok.append(
						    f'{ctx.author.mention} - Epic:\"{nev}\" - Konzol:\"{psnev}\"'
						)
						print(
						    f'PS - Sorsolásra jelentkezett: {ctx.author}. Epic név: \"{nev}\" - Konzol tag: \"{psnev}\"'
						)
						await ctx.send(
						    f'Sorsolásra feliratkozott: {user}, a következő névvel: \"{nev}\" és konzol taggel: \"{psnev}\"'
						)
				else:
					await ctx.send(
					    f'Ezzel a konzol azonosítóval már jelentkeztek a sorsolásra. {user}'
					)
			else:
				await ctx.send(
				    f'Ezzel az EPIC felhasználónévvel jelentkeztek. {user}')
		else:
			await ctx.send(f'Már jelentkeztél a sorsolásra. {user}')
	else:
		await ctx.send(f'Téged ebben a körben már kisorsoltak. {user}')


@jelentkez.error
async def jelentkez_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'{ctx.author.mention} nem adtál meg nevet.')
	if isinstance(error, commands.CheckFailure):
		await ctx.send(
		    f'{ctx.author.mention} a jelentkezések ki vannak kapcsolva.')


#CREDIT
@bot.command()
async def credit(ctx):
	await ctx.send(
	    'Készítő: <@216965188606361611>\n\nNe felejtsétek el támogatni Ghost4Rider-t a S-A-C kódjával!'
	)


#ADMIN PARANCSOK


#ÁLLAPOT
@bot.command(aliases=['állapot', 'state'])
@commands.has_permissions(administrator=True)
async def allapot(ctx):
	if bot.isItOn == True:
		await ctx.send('A jelentkezések nyitva.')
	else:
		await ctx.send('A jelentkezések zárva.')


#BEKAPCSOL
@bot.command(aliases=['bekapcs', 'felkapcsol', 'felkapcs'])
@commands.has_permissions(administrator=True)
async def bekapcsol(ctx):
	bot.isItOn = True
	await ctx.send('Jelentkezések nyitva! @everyone')


#KIKAPCSOL
@bot.command(aliases=['kikapcs', 'lekapcsol', 'lekapcs'])
@commands.has_permissions(administrator=True)
async def kikapcsol(ctx):
	bot.isItOn = False
	await ctx.send('Jelentkezések bezárva! @everyone')


#TISZTIT
@bot.command(aliases=["tisztít", "clear", "delete"])
@commands.has_permissions(administrator=True, manage_messages=True)
async def tisztit(ctx, amount=10):
	print(f'\n{ctx.author} kitörölt {amount} üzenetet.')
	await ctx.channel.purge(limit=amount + 1)


#UJRA
@bot.command(aliases=["újra", "restart"])
@commands.has_permissions(administrator=True)
async def ujra(ctx):
	print(f'\n{ctx.author} törölte az összes jelentkezőt.')
	bot.jelentkezok.clear()
	bot.nyertesek.clear()
	await ctx.send("A jelentkezők törölve.")


#JELENTKEZOK
@bot.command(aliases=["jelentkezők"])
@commands.has_permissions(administrator=True)
async def jelentkezok(ctx):
	if len(bot.jelentkezok) != 0:
		print(f'\nJelentkezők száma: {len(bot.jelentkezok)}\nJelentkezők:')
		print('    |-|    '.join(bot.jelentkezok))
		await ctx.send('Jelentkezők:')
		await ctx.send(f'    |-|    '.join(bot.jelentkezok))
	else:
		print('\nNincsenek jelentkezők.\n')
		await ctx.send('Nincsenek jelentkezők.')


#NYERTESEK
@bot.command()
@commands.has_permissions(administrator=True)
async def nyertesek(ctx):
	if len(bot.nyertesek) > 0:
		print('\nNyertesek:')
		print('\n'.join(bot.nyertesek))
		await ctx.send('\n'.join(bot.nyertesek))
		await ctx.author.send('Nyertesek:')
		await ctx.author.send('\n'.join(bot.nyertesek))
	else:
		await ctx.send('Még nem volt sorsolás.')


#SORSOL
@bot.command()
@commands.has_permissions(administrator=True)
async def sorsol(ctx, amount=15):
	if (amount > len(bot.jelentkezok)) == False:
		print(f'\n{ctx.author} elkezdett egy sorsolást.')
		bot.nyertesek = random.sample(bot.jelentkezok, amount)
		for i in bot.nyertesek:
			bot.jelentkezok.remove(i)
		await ctx.send('Nyertesek:')
		await ctx.send('\n'.join(bot.nyertesek))
	else:
		await ctx.send('Hiba. Kevesebb a jelentkező, mint a sorsolni kívánt személy.')
		print(
		    'Sorsolási hiba: Kevesebb a jelentkező mint a sorsolni kívánt személy.'
		)


#ADMIN PARANCSOK
@bot.command(
    aliases=["admin", "admin_control", "admin control", "admin parancsok"])
@commands.has_permissions(administrator=True)
async def admin_parancsok(ctx):
	await ctx.author.send(
	    "Admin parancsok:\n```!lotbot sorsol <kisorsoltak száma>\nKisorsolja a megadott számnyi jelentkezőt. (Ha nem írsz be számot akkor 15 darabot alapból.)``````!lotbot jelentkezok\nKiírja a jelentkezőket.``````!lotbot ujra\nKiüríti a jelentkező listát.``````!lotbot tisztit <törölni kívánt üzenetek száma>\nKitörli a megadottnyi üzenetet a szobában. (Ha nem írsz be számot alapértelmezetten 10-et.)``````!lotbot allapot - Kiírja a jelentkezések állapotát.``````!lotbot bekapcsol - Engedélyezi a jelentkezéseket.``````!lotbot kikapcsol - Lezárja a jelentkezéseket.``````!lotbot kidob <@felhasználó> - Kidobja a felhasználót a jelentkezők közül.```"
	)


#KIDOB
@bot.command()
@commands.has_permissions(administrator=True)
async def kidob(ctx, user: discord.Member):
	userId = str(user.id)
	print(user)
	isnotJoined = True
	for i in bot.jelentkezok:
		print(i)
		if i.__contains__(userId):
			del bot.jelentkezok[bot.jelentkezok.index(i)]
			isnotJoined = False
			await ctx.send(
			    f'{user.mention} kidobva a sorsolásból! {ctx.author.mention}')
	if isnotJoined:
		await ctx.send(
		    f'{user.mention} még nem jelentkezett sorsolásra. {ctx.author.mention}'
		)


#DEBUG PARANCSOK
def isCreator(ctx):
	return ctx.author.id == 216965188606361611


@bot.command()
@commands.check(isCreator)
async def debug_iam(ctx):
	print(ctx.author)
	print(ctx.author.mention)
	print(bot.jelentkezok)


@bot.command()
@commands.check(isCreator)
async def debug_jelentkezok(ctx):
	print(bot.jelentkezok)
	await ctx.send(bot.jelentkezok)


@bot.command()
@commands.check(isCreator)
async def debug_jeldel(ctx, index: int):
	if len(bot.jelentkezok) >= index:
		print(f'{bot.jelentkezok[index]} jelentkező')
		print(index)
		del bot.jelentkezok[index]
		print('Jelentkező törölve')
	else:
		await ctx.author.send('Hiba')


@bot.command()
@commands.check(isCreator)
async def debug_jel(ctx, nev, psnev=""):
	nev = nev.replace('<space>', ' ')
	psnev = psnev.replace('<space>', ' ')
	if len(psnev) == 0:
		bot.jelentkezok.append(f'{ctx.author.mention} - Epic:\"{nev}\"')
		print(
		    f'PC - Sorsolásra jelentkezett: {ctx.author}. Epic név: \"{nev}\"')
		await ctx.send(
		    f'Sorsolásra feliratkozott: {ctx.author.mention}, a következő névvel: \"{nev}\"'
		)
	else:
		bot.jelentkezok.append(
		    f'{ctx.author.mention} - Epic:\"{nev}\" - Konzol:\"{psnev}\"')
		print(
		    f'PS - Sorsolásra jelentkezett: {ctx.author}. Epic név: \"{nev}\" - Konzol tag: \"{psnev}\"'
		)
		await ctx.send(
		    f'Sorsolásra feliratkozott: {ctx.author.mention}, a következő névvel: \"{nev}\" és konzol taggel: \"{psnev}\"'
		)


#ACTIVE BOT:
bot.run("token")
