import os
from datetime import date
import textwrap
import warnings
import markdown2
from flask import Flask, render_template, request, Response, session, redirect, url_for
from flask_session import Session

# Importações do Google GenAI e ADK
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types as genai_types

warnings.filterwarnings("ignore")

# --- Configuração da Aplicação Flask ---
app = Flask(__name__)

# ATENÇÃO: Configure sua GOOGLE_API_KEY!
# 1. Crie um arquivo chamado .env na raiz do seu projeto.
# 2. Adicione a seguinte linha ao arquivo .env:
#    GOOGLE_API_KEY="SUA_CHAVE_API_AQUI_DO_GOOGLE_AI_STUDIO"
# 3. Instale python-dotenv: pip install python-dotenv
# 4. O código abaixo carregará a variável de ambiente.
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.environ.get("GOOGLE_API_KEY")
print(f"Valor da GOOGLE_API_KEY carregada: {google_api_key}")
if not google_api_key:
    # Em um ambiente de produção, você pode querer lançar um erro ou logar.
    # Para este exemplo, vamos imprimir um aviso.
    print("AVISO: A variável de ambiente GOOGLE_API_KEY não foi definida. A aplicação pode não funcionar corretamente.")
    # Se a chave for absolutamente necessária para a inicialização do cliente,
    # o SDK do genai pode falhar mais tarde.
    # genai.configure(api_key=google_api_key) # O SDK geralmente pega da env var automaticamente

# Configurar a chave secreta para a sessão do Flask e o tipo de sessão
app.config["SECRET_KEY"] = os.urandom(24)  # Chave secreta para segurança da sessão
app.config["SESSION_TYPE"] = "filesystem"  # Armazena dados da sessão no sistema de arquivos
app.config["SESSION_PERMANENT"] = False # Sessões não são permanentes por padrão
app.config["SESSION_USE_SIGNER"] = True # Assina cookies de sessão
# app.config["SESSION_FILE_DIR"] = './.flask_session/' # Opcional: especifica diretório para arquivos de sessão
Session(app)


# --- Definição do Modelo de IA ---
IA_MODEL = 'gemini-2.0-flash' # Modelo atualizado, verifique a disponibilidade

# --- Funções Adaptadas do Notebook ---

def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    user_session_id = session.get('_id', 'session_default')
    current_session = session_service.create_session(
        app_name=agent.name, user_id="web_user", session_id=user_session_id
    )
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="web_user", session_id=user_session_id, new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text
                    final_response += "\n"
    return final_response.strip()

def convert_text_to_html(text_content: str) -> str:
    if not text_content:
        return ""
    text_content = text_content.replace('•', '*')
    html_content = markdown2.markdown(
        text_content,
        extras=["tables", "fenced-code-blocks", "break-on-newline", "strike", "smarty-pants"]
    )
    return html_content

# --- Agente 1: Pesquisador de Projetos Sociais ---
def pesquisador_social(localizacao: str, data_de_hoje: str) -> str:
    pesquisador = Agent(
        name="pesquisador_social_web", 
        model=IA_MODEL,
        description="agente que pesquisa sobre ações sociais na região",
        tools=[google_search],
        instruction="""Você é um especialista em projetos sociais. Sua responsabilidade é identificar a região e estudar sobre
        os possíveis projetos sociais, voluntariado, ações sociais etc. que podem estar acontecendo na região.
        Você deve retornar uma lista com os projetos encontrados. Caso existam inscrições, fornecer data de abertura e data limite também.
        Preciso que você também de sugestões de possíveis projetos sociais para se criar na região, baseado no que foi encontrado e o que não foi encontrado, mas que gerariam impacto para a população.
        Caso não encontre nenhum projeto, retorne uma mensagem informando que não encontrou nenhum projeto.
        Formate sua resposta usando Markdown para melhor legibilidade (títulos, listas, negrito).
        """
    )
    entrada_para_pesquisa = f"Localização: {localizacao}\nData de hoje: {data_de_hoje}"
    projetos_achados = call_agent(pesquisador, entrada_para_pesquisa)
    return projetos_achados

# --- Agente 2: Organizador de Projetos Sociais ---
def organizador_social(localizacao: str, projetos_achados: str) -> str:
    organizador = Agent(
        name="organizador_social_web",
        model=IA_MODEL,
        description="organiza e filtra a lista de projetos encontrados",
        tools=[google_search],
        instruction="""Você é um organizador de projetos sociais. Sua responsabilidade é receber os projetos encontrados, analisar e filtrá-los por área
        para que o usuário consiga localizar, de forma clara, quais projetos fazem mais sentido pra ele. Você deve retornar uma lista com os projetos encontrados, filtrados por área, com título, descrição, se possível incluir telefone para contato com os responsáveis.
        Caso exista, aplique também as datas necessárias, como data de abertura e data limite de inscrição.
        Formate sua resposta usando Markdown para melhor legibilidade (títulos, listas, negrito).
        """
    )
    entrada_para_organizacao = f"Localização: {localizacao}\nProjetos encontrados anteriormente: {projetos_achados}"
    projetos_organizados = call_agent(organizador, entrada_para_organizacao)
    return projetos_organizados

# --- Agente 3: Criação de arquivos CSV ---
def analista_social(localizacao: str, projetos_organizados: str) -> dict:
    analista = Agent(
        name="analista_social_web",
        model=IA_MODEL,
        description="Analisa e cria arquivos csv para usuário final",
        tools=[],
        instruction="""Você é um analista social e sua função é prover um arquivo csv para o usuário final com os projetos organizados.
        Sua resposta DEVE ser formatada EXATAMENTE como o conteúdo de um arquivo CSV válido.
        O separador deve ser vírgula (,).
        A primeira linha DEVE ser o cabeçalho com os nomes das colunas (por exemplo: Titulo,Descricao,AreaSocial,PublicoAlvo,TelefoneContato,DataAberturaInscricao,DataLimiteInscricao,StatusProjeto).
        StatusProjeto pode ser 'Existente' ou 'Sugestão'.
        Você também deve separar no arquivo projetos que estão acontecendo e projetos que podem ser criados (sugestões).
        Cada linha subsequente deve representar um projeto, com os detalhes separados por vírgulas, na mesma ordem do cabeçalho.
        Use aspas duplas ("") para envolver campos que possam conter vírgulas ou quebras de linha, se necessário, conforme o padrão CSV.
        Não inclua nenhum texto adicional antes ou depois do conteúdo CSV. Apenas o CSV.
        Se não houver projetos ou sugestões, retorne apenas o cabeçalho.
        """
    )
    entrada_para_criacao = f"Localização: {localizacao}\nProjetos e Sugestões (já organizados): {projetos_organizados}"
    criacao_arquivo_csv_content = call_agent(analista, entrada_para_criacao)

    # Limpeza básica para garantir que é apenas CSV
    # Remove linhas em branco no início/fim e garante que comece com o cabeçalho esperado
    lines = criacao_arquivo_csv_content.strip().split('\n')
    if not lines or not lines[0].lower().startswith("titulo"): # Checagem simples do cabeçalho
        # Se a resposta não parecer um CSV, pode ser uma mensagem de erro do agente
        # ou uma formatação inesperada. Retornar um CSV vazio ou um erro.
        print(f"Resposta inesperada do agente analista (esperava CSV): {criacao_arquivo_csv_content}")
        # Pode ser melhor retornar um CSV com apenas cabeçalho ou uma mensagem de erro específica.
        # Para este exemplo, vamos retornar o que veio, mas logamos o aviso.
        pass


    nome_arquivo = f"projetos_sociais_{localizacao.replace(' ', '_').lower()}.csv"
    return {"filename": nome_arquivo, "csv_content": criacao_arquivo_csv_content.strip()}

# --- Rotas da Aplicação Flask ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        localizacao = request.form.get('localizacao')
        if not localizacao:
            return render_template('index.html', error="Por favor, insira uma localização.")

        data_de_hoje = date.today().strftime("%d/%m/%Y")
        resultados_processamento = {} # Dicionário para armazenar todos os resultados

        try:
            # Limpar dados da sessão anterior para CSV
            session.pop('csv_content', None)
            session.pop('csv_filename', None)

            resultados_processamento['localizacao'] = localizacao

            # Etapa 1: Pesquisador Social
            # Usamos um sufixo _raw para o texto puro e _html para o convertido
            projetos_achados_raw = pesquisador_social(localizacao, data_de_hoje)
            if not projetos_achados_raw: # Se o agente não retornar nada
                 projetos_achados_raw = "Nenhum projeto encontrado ou sugestão fornecida pelo pesquisador."
            resultados_processamento['projetos_achados_html'] = convert_text_to_html(projetos_achados_raw)

            # Etapa 2: Organizador Social
            # Passa o resultado raw do pesquisador para o organizador
            organizacao_projetos_raw = organizador_social(localizacao, projetos_achados_raw)
            if not organizacao_projetos_raw:
                organizacao_projetos_raw = "Nenhuma organização de projetos foi fornecida."
            resultados_processamento['organizacao_projetos_html'] = convert_text_to_html(organizacao_projetos_raw)

            # Etapa 3: Analista Social (Gerar CSV)
            # Passa o resultado raw do organizador para o analista
            csv_data = analista_social(localizacao, organizacao_projetos_raw)
            session['csv_content'] = csv_data['csv_content']
            session['csv_filename'] = csv_data['filename']
            resultados_processamento['csv_filename'] = csv_data['filename']
            resultados_processamento['csv_disponivel'] = bool(csv_data['csv_content'] and not csv_data['csv_content'].isspace() and len(csv_data['csv_content'].splitlines()) > 1)


            return render_template('resultados.html', resultados=resultados_processamento)

        except Exception as e:
            print(f"Erro durante o processamento da solicitação: {e}") # Log do erro no servidor
            # Em caso de erro com a API do Google ou outra exceção crítica:
            if "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
                 error_message = "Erro: A chave da API do Google não é válida ou expirou. Verifique sua configuração."
            elif "RateLimitExceeded" in str(e):
                 error_message = "Erro: Limite de taxa da API excedido. Tente novamente mais tarde."
            else:
                 error_message = f"Ocorreu um erro inesperado ao processar sua solicitação. Detalhes: {str(e)}"
            return render_template('index.html', error=error_message, localizacao_anterior=localizacao)

    return render_template('index.html')

@app.route('/download_csv')
def download_csv():
    csv_content = session.get('csv_content')
    csv_filename = session.get('csv_filename', 'projetos_sociais.csv')

    if csv_content is None or csv_content.isspace():
        # Redirecionar para a home ou mostrar um erro se não houver CSV na sessão
        # return "Nenhum arquivo CSV para baixar ou o conteúdo está vazio.", 404
        return redirect(url_for('index', error="Conteúdo do CSV não encontrado para download."))


    # Garante que o conteúdo seja bytes para a Response
    if isinstance(csv_content, str):
        csv_bytes = csv_content.encode('utf-8')
    else:
        csv_bytes = csv_content # Se já for bytes

    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"{csv_filename}\"",
            "Content-Type": "text/csv; charset=utf-8" # Especifica charset
        }
    )

# --- Execução da Aplicação ---
if __name__ == '__main__':
   
    session_file_dir = os.path.join(os.path.dirname(__file__), '.flask_session')
    if not os.path.exists(session_file_dir):
        os.makedirs(session_file_dir)
    app.config["SESSION_FILE_DIR"] = session_file_dir

    app.run(debug=True) # debug=True é útil para desenvolvimento
