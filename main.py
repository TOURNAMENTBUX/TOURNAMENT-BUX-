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

# --- LOJA TOURNAMENT BUX - GIFT CARD ---
PRODUTOS = {
    "500": {"nome": "Gift Card 500 Robux", "preco": 28.33, "estoque": 1, "emoji": "🎁"},
    "1000": {"nome": "Gift Card 1000 Robux", "preco": 53.33, "estoque": 1, "emoji": "🎁"},
    "1500": {"nome": "Gift Card 1500 Robux", "preco": 78.33, "estoque": 1, "emoji": "🎁"},
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
                return await interaction.response.send_message("Esse Gift Card esta SEM ESTOQUE no momento! A loja esta em reabastecimento, volta ja ja!", ephemeral=True)
            embed = discord.Embed(
                title="Pedido Criado - Tournament Bux",
                description=f"Voce selecionou **{produto['nome']}**\n\n**Valor: R$ {produto['preco']:.2f}**\n\n**Pague com Pix:**\n`{PIX_CHAVE}`\n\n1. Faca o Pix\n2. Mande o comprovante aqui\n3. Aguarde a entrega!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        return comprar_callback

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot {bot.user} ONLINE! Prefix: /")

@bot.tree.command(name="loja", description="Ver a loja Tournament Bux")
async def loja(interaction: discord.Interaction):
    embed = discord.Embed(title="LOJA TOURNAMENT BUX", description="Clique no Gift Card que deseja comprar!", color=0xFFD700)
    for cod, info in PRODUTOS.items():
        if info["estoque"] > 0:
            status = f"R$ {info['preco']:.2f} | Estoque: {info['estoque']}"
        else:
            status = "SEM ESTOQUE - EM REABASTECIMENTO"
        embed.add_field(name=f"{info['emoji']} {info['nome']}", value=status, inline=False)
    await interaction.response.send_message(embed=embed, view=LojaView())

bot.run(TOKEN)
