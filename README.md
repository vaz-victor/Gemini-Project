# Imersão IA Alura + Google - Assistente Social

Uma aplicação web para conectar pessoas a projetos e ações sociais em sua região, facilitando o voluntariado e o impacto positivo.

✨ **Sobre o Projeto**

Este projeto foi desenvolvido durante o curso IMERSÃO IA da Alura, em colaboração com o Google. O principal objetivo era desenvolver um agente baseado em IA que pudesse fornecer insights e informações relevantes para pessoas que desejam fazer voluntariado ou participar de alguma ação social em sua comunidade, mas não sabem por onde começar. A ideia é facilitar essa procura através de uma interface web intuitiva e fornecer os materiais necessários (como uma lista organizada e um arquivo CSV) para que o usuário tenha opções de acordo com seus interesses e disponibilidade, gerando impacto social onde quer que esteja.

**Considerações**

* Foi desenvolvido para ser utilizado tanto em ambientes profissionais como pessoais, sem restrições.
* O foco é democratizar o acesso à informação sobre oportunidades de engajamento social.
* Estou providênciando o projeto de 2 maneiras
    - Arquivo comentado linha por linha do Google Colab - Projeto-Alura-AgenteSocial.ipynb - Para quem quer ter um entendimento melhor do que cada linha está fazendo.
    - App usando Flask, transformando o código e trazendo uma experiência visual (web) do assistente.
* Para quem não conseguir executar, a pasta IMAGENS trará um overview de como o programa funciona em uma interface web.


🎯 **Funcionalidades**

O projeto utiliza uma sequência de agentes de IA para processar a solicitação do usuário:

* **Agente Pesquisador:** Realiza a pesquisa e coleta de informações sobre projetos sociais, voluntariado e ações sociais disponíveis em uma localização específica fornecida pelo usuário.
* **Agente Organizador:** Recebe as informações coletadas pelo Agente Pesquisador, analisa, filtra e organiza os projetos encontrados por área social, fornecendo detalhes como título, descrição e, se possível, contatos e datas de inscrição.
* **Agente Criador:** Processa a lista organizada de projetos e gera um arquivo no formato CSV, pronto para download, contendo todos os detalhes dos projetos encontrados e sugestões, separados por colunas para fácil análise.

🛠️ **Tecnologias Utilizadas**

* **Linguagem:** Python (v3.13), HTML, CSS, JAVASCRIPT
* **Frameworks/Bibliotecas Principais:**
    * Flask (para a aplicação web)
    * Flask-Session (para gerenciamento de sessão)
    * `google-generativeai` (SDK do Google AI)
    * `google-adk` (Agent Development Kit)
    * `markdown2` (para converter Markdown em HTML)
    * `python-dotenv` (para carregar variáveis de ambiente)
    * `requests` (dependência do ADK/GenAI)
* **Serviços Google:**
    * Google AI Studio (para configuração, API KEY)
    * Google Gemini - Flash 2.0 (modelo de IA utilizado)

📋 **Pré-requisitos**

Antes de começar, você precisará ter instalado em sua máquina:

* Python 3.13
* Uma chave de API válida do Google AI Studio.

⚙️ **Instalação e Configuração**

Siga os passos abaixo para configurar o ambiente de desenvolvimento:

1.  **Clone o repositório:**

    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_AQUI]
    cd NOME-DO-PROJETO # Substitua pelo nome da pasta do seu projeto
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**

    ```bash
    python -m venv venv
    # No Windows:
    # venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure a variável de ambiente `GOOGLE_API_KEY`:**
    Crie um arquivo `.env` na raiz do projeto e adicione a seguinte linha, substituindo `SUA_CHAVE_API_AQUI_DO_GOOGLE_AI_STUDIO` pela sua chave obtida no Google AI Studio:

    ```
    GOOGLE_API_KEY="SUA_CHAVE_API_AQUI_DO_GOOGLE_AI_STUDIO"
    ```

▶️ **Executando o Projeto**

Para iniciar a aplicação web, execute o seguinte comando no terminal, dentro da pasta do projeto e com o ambiente virtual ativado:

```bash
python app.py
