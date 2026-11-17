import discord
from discord.ext import commands
from discord.ui import View, Button
import os

TOKEN = os.getenv("TOKEN")
PIX_CHAVE = os.getenv("PIX_CHAVE")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ========== IDS DO TOURNAMENT BUX ==========
CANAL_VERIFICACAO = 1572222595917422704
CANAL_BOAS_VINDAS = 1572247089025654895
CANAL_REGRAS = 1572223452247629945
CARGO_VERIFICADO = 1572250595447013599
CATEGORIA_TICKET = 0

@bot.event
async def on_ready():
    print(f"TOURNAMENT BUX online! {bot.user}")

# ========== 1. VERIFICAÇÃO + BOAS-VINDAS ==========
class VerificarView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verificar ✅", style=discord.ButtonStyle.green)
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        cargo = interaction.guild.get_role(CARGO_VERIFICADO)
        if cargo in interaction.user.roles:
            await interaction.response.send_message("Você já está verificado! ✅", ephemeral=True)
            return
        await interaction.user.add_roles(cargo)
        await interaction.response.send_message("Você foi verificado! ✅ Agora você tem acesso ao servidor!", ephemeral=True)

        canal = bot.get_channel(CANAL_BOAS_VINDAS)
        embed = discord.Embed(
            title=f"👋 Bem-vindo(a), {interaction.user.name}!",
            description=f"Seja bem-vindo ao **TOURNAMENT BUX**! 🎉\n\n📜 Leia as regras em <#{CANAL_REGRAS}>\n📖 Veja como comprar em <#guia>\n🛒 Produtos em <#comprar>",
            color=0x5865F2
        )
        if interaction.user.avatar:
            embed.set_thumbnail(url=interaction.user.avatar.url)
        await canal.send(embed=embed)

@bot.command()
async def setup_verificacao(ctx):
    embed = discord.Embed(title="✅ Verificação - TOURNAMENT BUX", description="Clique no botão abaixo para se verificar e liberar o acesso ao servidor!", color=0x00ff00)
    await ctx.send(embed=embed, view=VerificarView())

# ========== 2. GUIA AUTOMÁTICO ==========
@bot.command()
async def setup_guia(ctx):
    embed = discord.Embed(title="📖 GUIA - COMO COMPRAR NO TOURNAMENT BUX", description="Siga o passo a passo, é bem simples!", color=0x5865F2)
    embed.add_field(name="1️⃣ Escolha o produto", value="Vá em <#comprar> e clique no Gift Card que você quer.", inline=False)
    embed.add_field(name="2️⃣ Abra um Ticket", value="Vá em <#ticket> e clique em **Abrir Ticket**.", inline=False)
    embed.add_field(name="3️⃣ Pagamento", value="A staff vai te atender no ticket. NUNCA passe sua chave PIX no canal público!", inline=False)
    embed.add_field(name="4️⃣ Receba!", value="Após o pagamento, você recebe seu Gift Card na hora! 🎉", inline=False)
    await ctx.send(embed=embed)

# ========== 3. TICKET ==========
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir Ticket 🎟️", style=discord.ButtonStyle.blurple)
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        for channel in guild.channels:
            if channel.name == f"ticket-{interaction.user.name.lower()}":
                await interaction.response.send_message(f"Você já tem um ticket! {channel.mention}", ephemeral=True)
                return
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        categoria = bot.get_channel(CATEGORIA_TICKET) if CATEGORIA_TICKET != 0 else None
        canal_ticket = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites, category=categoria)
        await canal_ticket.send(f"{interaction.user.mention} Descreva o que você quer comprar!", view=FecharView())
        await interaction.response.send_message(f"Ticket criado! {canal_ticket.mention}", ephemeral=True)

class FecharView(View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Fechar Ticket 🔒", style=discord.ButtonStyle.red)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fechando...", ephemeral=True)
        await interaction.channel.delete()

@bot.command()
async def setup_ticket(ctx):
    embed = discord.Embed(title="🎟️ Suporte - TOURNAMENT BUX", description="Clique para abrir um ticket!", color=0xff0000)
    await ctx.send(embed=embed, view=TicketView())

# ========== 4. SUA LOJA ORIGINAL - NÃO APAGAR ==========
PRODUTOS = {
    "500": {"nome": "Gift Card 500 Robux", "preco": 28.33, "estoque": 1, "emoji": "🎮"},
    "1000": {"nome": "Gift Card 1000 Robux", "preco": 53.33, "estoque": 1, "emoji": "🎮"},
    "1500": {"nome": "Gift Card 1500 Robux", "preco": 78.33, "estoque": 1, "emoji": "🎮"},
}

class LojaView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for cod, prod in PRODUTOS.items():
            if prod["estoque"] > 0:
                label = f"{prod['nome']} - R$ {prod['preco']:.2f}"
                style = discord.ButtonStyle.green
                disabled = False
            else:
                label = f"{prod['nome']} - SEM ESTOQUE"
                style = discord.ButtonStyle.gray
                disabled = True
            btn = Button(label=label, style=style, emoji=prod["emoji"], disabled=disabled)
            btn.callback = self.criar_callback(cod, prod)
            self.add_item(btn)

    def criar_callback(self, cod, produto):
        async def comprar_callback(interaction: discord.Interaction):
            if produto["estoque"] <= 0:
                return await interaction.response.send_message("Esse Gift Card esta SEM ESTOQUE!", ephemeral=True)
            embed = discord.Embed(
                title="Pedido Criado - Tournament Bux",
                description=f"Voce selecionou **{produto['nome']}**\n**Valor: R$ {produto['preco']:.2f}**\n\nAbra um ticket em <#ticket> para finalizar a compra e receber sua chave PIX!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        return comprar_callback

@bot.command()
async def setup_loja(ctx):
    embed = discord.Embed(title="🛒 Loja - TOURNAMENT BUX", description="Escolha seu Gift Card abaixo!", color=0x5865F2)
    await ctx.send(embed=embed, view=LojaView())

# ========== FINAL SEGURO ==========
bot.run(TOKEN)
