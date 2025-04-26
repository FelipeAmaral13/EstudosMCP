
# 🌎 MCP City Weather

> Um projeto de integração de agentes de IA com o mundo real, usando o protocolo **MCP (Model Context Protocol)**.

---

## 📚 Sobre o Projeto

O **MCP City Weather** é uma aplicação que demonstra como criar servidores MCP para expor ferramentas que modelos de linguagem (LLMs) como Claude ou ChatGPT possam utilizar de forma dinâmica.

Este projeto disponibiliza duas funcionalidades:
- **Latitude e Longitude** de qualquer cidade
- **Clima Atual** (temperatura e descrição climática) da cidade informada

Utilizando o protocolo MCP, os agentes conseguem descobrir e utilizar essas ferramentas sem necessidade de programação manual extra, aumentando a automação e a inteligência operacional.

---

## ⚙️ Tecnologias e Conceitos Utilizados

- [Python 3.11+](https://www.python.org/)
- [MCP (Model Context Protocol)](https://pypi.org/project/mcp/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Nominatim API (OpenStreetMap)](https://nominatim.openstreetmap.org/)
- [Claude Desktop (opcional para uso de agentes)]

---

## 🚀 Funcionalidades Implementadas

| Nome da Ferramenta | Descrição |
|:-------------------|:----------|
| `LatLon`            | Consulta latitude e longitude da cidade informada |
| `WeatherNow`        | Retorna o clima atual (temperatura e descrição) da cidade informada |

---

## 🔥 Como Rodar o Projeto

O projeto utiliza o **uv** como gerenciador de pacotes — uma alternativa mais rápida e moderna ao `pip`.

### 1. Instalar o `uv`

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Ou consulte a documentação oficial: [uv - Astral](https://astral.sh/docs/uv)

### 2. Clonar este Repositório

```bash
git clone https://github.com/FelipeAmaral13/EstudosMCP/mcp-city-weather.git
cd mcp-city-Weather
```

### 3. Instalar as Dependências

```bash
uv pip install -r requirements.txt
```

### 4. Configurar o `.env`

Crie um arquivo `.env` na raiz do projeto com o conteúdo:

```dotenv
OPENWEATHER_API_KEY=SEU_TOKEN_OPENWEATHER
```

> ⚡ Veja abaixo como obter seu token da OpenWeather!

---

## 🌤️ Como obter a API Key do OpenWeather

1. Acesse [https://openweathermap.org/api](https://openweathermap.org/api)
2. Crie uma conta gratuita
3. No painel do usuário, gere uma nova **API Key**
4. Copie a chave e cole no arquivo `.env` como mostrado acima.

---

## 🛠️ Como Rodar o MCP Server

O servidor MCP é responsável por expor as ferramentas para uso pelos agentes de IA.

### Para rodar o servidor:

```bash
uv run server/lat_lon_weather_server.py
```

O servidor utilizará o transporte `stdio` (comunicação direta com clientes ou Claude Desktop).

---

## 🖥️ Como Rodar o MCP Client

O client é usado para interagir com o servidor de forma manual (útil para testes ou demonstrações).

### Para rodar o cliente:

```bash
uv run client/lat_lon_weather_client.py
```

O cliente vai solicitar:
- Nome da cidade
- Escolha entre:
  - Obter latitude/longitude
  - Obter clima atual

---

## 📦 Estrutura do Projeto

```bash
📦 mcp-city-weather
 ┣ 📂 server
 ┃ ┗ 📜 lat_lon_weather_server.py
 ┣ 📂 client
 ┃ ┗ 📜 lat_lon_weather_client.py
 ┣ 📜 .env.example
 ┣ 📜 README.md
 ┣ 📜 requirements.txt
```

---

## 🧠 O que é MCP?

O **Model Context Protocol (MCP)** é um protocolo que permite que **modelos de linguagem (LLMs)** descubram e utilizem ferramentas externas de forma padronizada e segura.

**Benefícios:**
- 🌎 Conectar LLMs ao mundo real
- 🛡️ Aumentar controle e segurança de chamadas de APIs
- 🏗️ Permitir automação dinâmica sem "gambiarras" de prompts
- ⚡ Integrar múltiplas fontes de dados em tempo real

O projeto atual é uma demonstração prática de como agentes podem consultar informações urbanas (geolocalização + clima) de forma fluída via MCP.

---

## ✅ Status do Projeto

> 🔵 Projeto funcional e pronto para ser integrado a agentes Claude, OpenAI Agents, CrewAI ou outros.

---

## 🛠️ Configurando o Claude Desktop para Uso do MCP

Para integrar seu MCP Server com o Claude Desktop e permitir que o modelo descubra e utilize as ferramentas `LatLon` e `WeatherNow`, siga os passos:

1. Instale e abra o Claude Desktop.
2. Localize o arquivo de configuração do Claude:
    - Windows: `%AppData%\Claude\claude_desktop_config.json`
    - MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Edite o arquivo adicionando ou atualizando a seção `"mcpServers"` para incluir seu projeto:

```json
{
    "mcpServers": {
        "CityServices": {
            "command": "uv",
            "args": [
                "--directory",
                "CAMINHO/DO/SEU/PROJETO/server",
                "run",
                "lat_lon_weather_server.py"
            ]
        }
    }
}
```

4. Substitua `CAMINHO/DO/SEU/PROJETO` pelo caminho completo onde seu projeto está salvo.
5. Reinicie o Claude Desktop.

Pronto! O Claude agora poderá listar automaticamente as ferramentas MCP disponíveis no seu projeto `CityServices` e utilizá-las conforme o contexto da conversa.

---

## 📬 Contato

Caso tenha interesse em parcerias, dúvidas técnicas ou colaboração:

**Felipe Meganha**  
[LinkedIn](https://www.linkedin.com/in/felipe-meganha/)  
[Substack](https://substack.com/@felipemeganha)

---

## 🛡️ Licença

Este projeto é licenciado sob os termos da licença MIT.