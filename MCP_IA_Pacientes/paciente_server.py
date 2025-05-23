import logging
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import gradio as gr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///pacientes.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class PacienteDB(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    idade = Column(Integer, nullable=False)
    sintoma = Column(String(255), nullable=False)
    data_internacao = Column(Date, nullable=False)
    data_alta = Column(Date, nullable=True)
    medico_responsavel = Column(String(100), nullable=False)

Base.metadata.create_all(bind=engine)
logger.info("✅ Banco de dados inicializado e tabelas criadas.")

class CadastroPaciente(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    idade: int = Field(..., gt=0, lt=130)
    sintoma: str = Field(..., min_length=3)
    data_internacao: Optional[date] = Field(default_factory=date.today)
    data_alta: Optional[date] = None
    medico_responsavel: str = Field(..., min_length=3)

    @model_validator(mode='after')
    def check_datas_coerentes(self):
        if self.data_internacao and self.data_alta and self.data_alta < self.data_internacao:
            logger.warning(f"❗ Inconsistência nas datas: {self.data_internacao} -> {self.data_alta}")
            raise ValueError("A data de alta não pode ser anterior à data de internação.")
        return self

def consultar_paciente(nome: str, idade: int, sintoma: Optional[str] = None, medico_responsavel: Optional[str] = None) -> str:
    db = SessionLocal()
    logger.info(f"🔍 Consultando paciente: {nome}, {idade} anos.")
    
    paciente_existente = db.query(PacienteDB).filter_by(nome=nome, idade=idade).first()
    
    if paciente_existente:
        db.close()
        logger.info(f"⚠️ Paciente já cadastrado: {nome}, {idade} anos.")
        return f"⚠️ Paciente '{nome}' com {idade} anos já está cadastrado."

    paciente = CadastroPaciente(
        nome=nome,
        idade=idade,
        sintoma=sintoma or "Não informado",
        medico_responsavel=medico_responsavel or "Não atribuído",
        data_internacao=date.today()
    )

    paciente_db = PacienteDB(
        nome=paciente.nome,
        idade=paciente.idade,
        sintoma=paciente.sintoma,
        data_internacao=paciente.data_internacao,
        data_alta=paciente.data_alta,
        medico_responsavel=paciente.medico_responsavel
    )

    db.add(paciente_db)
    db.commit()
    db.close()

    logger.info(f"✅ Paciente cadastrado: {paciente.nome}, {paciente.idade} anos.")

    return (f"✅ Paciente cadastrado:\n"
            f"🧑‍⚕️ {paciente.nome} — {paciente.idade} anos\n"
            f"🩺 Sintoma: {paciente.sintoma}\n"
            f"🧑‍⚕️ Médico Responsável: {paciente.medico_responsavel}\n"
            f"🏥 Data de Internação: {paciente.data_internacao.isoformat()}")

def listar_pacientes() -> str:
    db = SessionLocal()
    logger.info("📋 Listando todos os pacientes.")
    
    pacientes = db.query(PacienteDB).all()
    db.close()

    if not pacientes:
        logger.info("📋 Nenhum paciente encontrado no banco.")
        return "📋 Nenhum paciente cadastrado."

    logger.info(f"📋 {len(pacientes)} paciente(s) listado(s).")
    return "\n\n".join([
        f"🧑‍⚕️ {p.nome} — {p.idade} anos | 🩺 {p.sintoma} | Médico: {p.medico_responsavel} | 🏥 {p.data_internacao.isoformat()}"
        for p in pacientes
    ])

with gr.Blocks() as demo:
    gr.Markdown("# 🏥 Servidor MCP - Cadastro de Pacientes")

    with gr.Tab("Cadastrar Paciente"):
        nome = gr.Textbox(label="Nome do Paciente")
        idade = gr.Number(label="Idade")
        sintoma = gr.Textbox(label="Sintoma (opcional)")
        medico = gr.Textbox(label="Médico Responsável (opcional)")
        botao = gr.Button("Cadastrar")
        saida = gr.Textbox(label="Confirmação")

        def cadastrar_gradio(nome, idade, sintoma, medico):
            try:
                logger.info(f"📥 Tentativa de cadastro via Gradio: {nome}, {idade} anos.")
                return consultar_paciente(nome, int(idade), sintoma, medico)
            except Exception as e:
                logger.exception("❌ Erro no cadastro de paciente.")
                return f"❌ Erro no cadastro: {str(e)}"

        botao.click(fn=cadastrar_gradio, inputs=[nome, idade, sintoma, medico], outputs=saida)

    with gr.Tab("Listar Pacientes"):
        saida_listagem = gr.Textbox(label="Pacientes Cadastrados", lines=10)
        btn_listar = gr.Button("Listar Todos")

        def listar_gradio():
            try:
                return listar_pacientes()
            except Exception as e:
                logger.exception("❌ Erro ao listar pacientes.")
                return f"❌ Erro na listagem: {str(e)}"

        btn_listar.click(fn=listar_gradio, outputs=saida_listagem)

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor Gradio na porta 7865 com MCP.")
    demo.launch(
        server_port=7865,
        mcp_server=True,
    )
