import os
import discord
from discord.ext import commands

TOKEN = os.environ.get("TOKEN")
PIX_CHAVE = "COLOQUE_SEU_PIX_AQUI"
COR = 0x8b00ff

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

PRODUTOS = {
    "500": ("500 Robux + Brinde", "R$ 28,33"),
    "1000": ("1000 Robux + Brinde", "R$ 53,33"),
    "1500": ("1500 Robux + Brinde", "R$ 78,33"),
}

class VerificarView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="✅ Verificar", style=discord.ButtonStyle.green, custom_id="verificar")
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        cargo = discord.utils.get(interaction.guild.roles, name="Verificado")
        if not cargo:
            cargo = await interaction.guild.create_role(name="Verificado")
        await interaction.user.add_roles(cargo)
        await interaction.response.send_message("✅ Você foi verificado! Canais liberados!", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📞 Chamar Equipe", style=discord.ButtonStyle.blurple, custom_id="chamar")
    async def chamar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user.mention} chamou a equipe!", ephemeral=False)
    @discord.ui.button(label="✅ Finalizar Ticket", style=discord.ButtonStyle.red, custom_id="fechar")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Fechando ticket em 5 segundos...")
        await interaction.channel.delete()

class MenuCompra(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="500 Robux + Brinde", description="R$ 28,33", emoji="💎", value="500"),
            discord.SelectOption(label="1000 Robux + Brinde", description="R$ 53,33", emoji="💰", value="1000"),
            discord.SelectOption(label="1500 Robux + Brinde", description="R$ 78,33", emoji="👑", value="1500"),
        ]
        super().__init__(placeholder="🛒 Clique aqui para selecionar...", options=options, custom_id="menu_compra")
    async def callback(self, interaction: discord.Interaction):
        nome, preco = PRODUTOS[self.values[0]]
        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, name="🎫 Tickets")
        if not categoria:
            categoria = await guild.create_category("🎫 Tickets")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        canal = await guild.create_text_channel(name=f"vendas-{interaction.user.name}", category=categoria, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Ticket criado! Vai pra {canal.mention}", ephemeral=True)
        embed = discord.Embed(title="🕐 PEDIDO PENDENTE - AGUARDANDO PAGAMENTO", description=f"Olá {interaction.user.mention}!", color=0xFFD700)
        embed.add_field(name="📦 Produto", value=nome, inline=False)
        embed.add_field(name="💰 Valor", value=preco, inline=False)
        embed.add_field(name="💳 Pix", value=f"`{PIX_CHAVE}`", inline=False)
        embed.add_field(name="📋 Próximo passo", value="1. Faça o Pix\n2. Mande o comprovante aqui\n3. Aguarde a entrega", inline=False)
        await canal.send(f"{interaction.user.mention} Ticket Criado!", embed=embed, view=TicketView())

class LojaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuCompra())

@bot.event
async def on_ready():
    bot.add_view(VerificarView())
    bot.add_view(LojaView())
    bot.add_view(TicketView())
    await bot.tree.sync()
    print(f"✅ {bot.user} ONLINE - Universal ATIVO!")

@bot.tree.command(name="verificacao", description="Postar o embed de verificação")
async def verificacao(interaction: discord.Interaction):
    embed = discord.Embed(title="✅ VERIFICAÇÃO", description="Clique no botão abaixo para liberar o servidor!", color=COR)
    await interaction.response.send_message(embed=embed, view=VerificarView())

@bot.tree.command(name="regras", description="Postar as regras")
async def regras(interaction: discord.Interaction):
    embed = discord.Embed(title="📜 REGRAS - TOURNAMENT BUX", description="1. Sem spam\n2. Respeite todos\n3. Sem golpes\n4. Mande o comprovante no ticket", color=COR)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="loja", description="Ver a loja")
async def loja(interaction: discord.Interaction):
    embed = discord.Embed(title="🛒 Tournament Bux - Loja", description="Selecione abaixo:", color=COR)
    embed.add_field(name="💎 500 Robux + Brinde", value="**R$ 28,33**", inline=False)
    embed.add_field(name="💰 1000 Robux + Brinde", value="**R$ 53,33**", inline=False)
    embed.add_field(name="👑 1500 Robux + Brinde", value="**R$ 78,33**", inline=False)
    await interaction.response.send_message(embed=embed, view=LojaView())

@bot.tree.command(name="guia", description="Como comprar")
async def guia(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 GUIA DE COMPRA", description="1. Vá em #comprar\n2. Escolha o produto\n3. Pague o Pix\n4. Mande o comprovante no ticket", color=COR)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticket", description="Abrir painel de ticket")
async def ticket(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 TICKET", description="Precisa de suporte? Clique abaixo!", color=COR)
    await interaction.response.send_message(embed=embed, view=TicketView())

bot.run(TOKEN)
