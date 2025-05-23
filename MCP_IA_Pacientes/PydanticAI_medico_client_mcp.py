import os
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Optional

import gradio as gr
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuração de ambiente
os.environ.setdefault("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

# Constantes
AVAILABLE_MODELS = ["llama-3.3-70b-versatile"]
SSE_URL = "http://127.0.0.1:7865/gradio_api/mcp/sse"

# Inicialização de servidor MCP
paciente_server = MCPServerHTTP(url=SSE_URL)
if hasattr(paciente_server, "client"):
    paciente_server.client.set_logging_level = lambda *args, **kwargs: None

class MCPAgentClient:
    """
    Interação com MCP e Groq Agent.
    """
    def __init__(self, model_name: str = AVAILABLE_MODELS[0]):
        self.model_name = model_name
        self.agent = self._create_agent(model_name)
        self.status_message = "Conectando ao servidor MCP..."

    def _create_agent(self, model_name: str) -> Agent:
        return Agent(
            f"groq:{model_name}",
            mcp_servers=[paciente_server],
            system="Você é um agente que responde sobre pacientes cadastrados."
        )

    def process_query(self, message: str, model_name: str) -> Tuple[str, Optional[float]]:
        """
        Processa uma consulta ao agente, com troca dinâmica de modelo.
        """
        if model_name != self.model_name:
            logger.info(f"Modelo alterado: {self.model_name} → {model_name}")
            self.model_name = model_name
            self.agent = self._create_agent(model_name)
        else:
            logger.info(f"Reutilizando modelo atual: {self.model_name}")

        self.status_message = f"Processando com modelo: {self.model_name}"

        try:
            with ThreadPoolExecutor() as executor:
                start_time = time.time()
                future = executor.submit(self._run_agent_sync, message)
                result = future.result(timeout=10.0)
                elapsed = time.time() - start_time

                self.status_message = f"Resposta em {elapsed:.2f}s"
                logger.info(f"Resposta recebida em {elapsed:.2f}s")

                return result, elapsed

        except asyncio.TimeoutError:
            self.status_message = "Timeout"
            logger.warning("Operação excedeu 10 segundos.")
            return "A operação demorou mais de 10s. Tente novamente.", None

        except Exception as e:
            self.status_message = f"Erro: {e}"
            logger.exception("Erro ao processar a consulta")
            return f"Erro: {e}", None

    def _run_agent_sync(self, message: str) -> str:
        """
        Executa o agente de forma síncrona dentro de um novo loop de evento.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self._run_agent_async(message))

    async def _run_agent_async(self, message: str) -> str:
        async with self.agent.run_mcp_servers():
            response = await self.agent.run(message)
            return response.output

    def get_status(self) -> str:
        return self.status_message

# Instância única para interação com o agente
agent_client = MCPAgentClient()

# Configuração da interface Gradio
with gr.Blocks(theme="soft") as demo:
    with gr.Row():
        gr.Markdown("## 🩺 Painel de Controle - Cliente MCP + Groq Agent")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Configurações")
            model_selector = gr.Dropdown(
                choices=AVAILABLE_MODELS, 
                label="Selecione o Modelo", 
                value=AVAILABLE_MODELS[0]
            )
            status_display = gr.Textbox(
                label="📡 Status do Sistema", 
                value=agent_client.get_status(), 
                interactive=False, 
                lines=2
            )

        with gr.Column(scale=2):
            gr.Markdown("### 💬 Interação com o Agente")
            chatbot = gr.Chatbot(
                label="Diálogo com o Agente",
                height=400,
                show_label=True,
                avatar_images=("user.png", "agent.png")  # opcional se tiver imagens
            )

            with gr.Row():
                user_input = gr.Textbox(
                    placeholder="Digite uma pergunta sobre pacientes...",
                    label="Mensagem"
                )
                send_button = gr.Button("📤 Enviar")

    # Função de resposta
    def respond(msg: str, history: list) -> tuple[str, list]:
        if not msg:
            return "", history
        try:
            history.append(["user", msg])
            response, _ = agent_client.process_query(msg, model_selector.value)
            history.append(["assistant", response])
        except Exception as e:
            logger.exception("Erro no processamento da mensagem")
            history.append(["assistant", f"⚠️ Erro: {str(e)}"])
        return "", history



    user_input.submit(respond, [user_input, chatbot], [user_input, chatbot])
    send_button.click(respond, [user_input, chatbot], [user_input, chatbot])

if __name__ == "__main__":
    logger.info("Iniciando cliente MCP via Gradio na porta 7860")
    demo.launch(server_port=7860)
