import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Carrega variáveis de ambiente (.env)
load_dotenv()

async def get_content(response) -> str:
    """Extrai conteúdo textual da resposta MCP"""
    if response.content and len(response.content) > 0:
        return response.content[0].text
    else:
        return "[Sem resposta do servidor]"

async def run_client():
    """Inicializa conexão MCP Client e executa ferramenta baseada na escolha"""
    server_params = StdioServerParameters(
        command="python",
        args=["E:\\Estudos\\MCP\\weatherNow_server\\lat_lon_weather_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n🚀 Bem-vindo ao MCP City Services")
            cidade = input("Informe o nome da cidade: ").strip()

            print("\nEscolha a operação:")
            print("1️⃣  Obter Latitude e Longitude")
            print("2️⃣  Obter Clima Atual")
            escolha = input("Digite 1 ou 2: ").strip()

            if escolha == "1":
                response = await session.call_tool("LatLon", {"cidade": cidade})
            elif escolha == "2":
                response = await session.call_tool("WeatherNow", {"cidade": cidade})
            else:
                print("[ERRO] Opção inválida. Encerrando o cliente.")
                return

            resultado = await get_content(response)
            print("\n🛰️ Resultado:")
            print(resultado)

if __name__ == "__main__":
    asyncio.run(run_client())
