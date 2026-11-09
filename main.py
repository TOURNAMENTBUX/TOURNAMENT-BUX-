import discord
from discord.ext import commands
from discord import app_commands
import os

PIX_CHAVE = "70b72ff2-ef70-487b-8f3f-eb6a96d56bb2"
PIX_NOME = "LUCAS DA SILVA"

PRODUTOS = {
    "bux100": {"nome": "100 Bux", "preco": 28.33},
    "bux200": {"nome": "200 Bux", "preco": 53.33},
    "bux300": {"nome": "300 Bux", "preco": 78.33},
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class LojaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="100 Bux - R$ 28,33", style=discord.ButtonStyle.green, custom_id="bux100")
    async def bux100(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.mostrar_pagamento(interaction, "bux100")

    @discord.ui.button(label="200 Bux - R$ 53,33", style=discord.ButtonStyle.blurple, custom_id="bux200")
    async def bux200(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.mostrar_pagamento(interaction, "bux200")

    @discord.ui.button(label="300 Bux - R$ 78,33", style=discord.ButtonStyle.red, custom_id="bux300")
    async def bux300(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.mostrar_pagamento(interaction, "bux300")

    async def mostrar_pagamento(self, interaction: discord.Interaction, produto_id: str):
        produto = PRODUTOS[produto_id]
        embed = discord.Embed(
            title=f"🛒 Você escolheu {produto['nome']}",
            description=f"**Valor:** R$ {produto['preco']:.2f}\n\n**1.** Faça o Pix para a chave abaixo\n**2.** Envie o comprovante aqui\n**3.** Aguarde a entrega do Produto",
            color=0x00ff00
        )
        embed.add_field(name="🔑 Chave Pix (Aleatória)", value=f"```{PIX_CHAVE}```", inline=False)
        embed.add_field(name="👤 Nome", value=PIX_NOME, inline=True)
        embed.add_field(name="💰 Valor exato", value=f"R$ {produto['preco']:.2f}", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comandos")
    except Exception as e:
        print(e)

@bot.tree.command(name="loja", description="Abrir a loja Tournament Bux")
async def loja(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏆 Tournament Bux - Loja Oficial",
        description="Escolha seu pacote abaixo e pague via Pix!",
        color=0xFFD700
    )
    embed.add_field(name="📦 100 Bux", value="R$ 28,33", inline=True)
    embed.add_field(name="📦 200 Bux", value="R$ 53,33", inline=True)
    embed.add_field(name="📦 300 Bux", value="R$ 78,33", inline=True)
    await interaction.response.send_message(embed=embed, view=LojaView())

bot.run(os.getenv("DISCORD_TOKEN"))
