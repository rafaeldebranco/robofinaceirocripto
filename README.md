# robofinanceirocripto

Um robô de trading automatizado para criptomoedas, desenvolvido em Python, utilizando a API da Crypto.com Exchange para operações de compra e venda, e registro de histórico.

## Visão Geral

Este projeto implementa um robô de trading básico para criptomoedas, focado em automatizar operações de compra e venda na Crypto.com Exchange. Ele foi projetado para ser extensível, permitindo que os usuários adicionem suas próprias estratégias de trading. O robô interage com a API privada da corretora para gerenciar a conta, obter informações de ordens e executar transações.

## Funcionalidades

*   **Conexão Segura:** Utiliza chaves de API e segredo para autenticação segura.
*   **Resumo da Conta:** Consulta o saldo e a disponibilidade de ativos na conta.
*   **Ordens Abertas:** Lista as ordens de compra e venda que ainda não foram executadas.
*   **Colocar Ordem:** Permite a criação de ordens de limite (compra/venda) para um par de negociação específico.
*   **Cancelar Ordem:** Cancela ordens abertas individualmente.
*   **Histórico de Operações:** (A ser implementado/expandido) A estrutura básica da API permite a consulta de histórico de ordens e transações.

## Pré-requisitos

Antes de começar, certifique-se de ter os seguintes softwares instalados:

*   **Python 3.11+**
*   **pip** (gerenciador de pacotes do Python)
*   **git** (para clonar o repositório)
*   **VS Code** (ambiente de desenvolvimento recomendado)

## Configuração do Ambiente

Siga os passos abaixo para configurar e executar o robô:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/robofinanceirocripto.git
    cd robofinanceirocripto
    ```
    (Substitua `seu-usuario` pelo seu nome de usuário do GitHub após a publicação)

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # venv\Scripts\activate   # No Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuração da API da Crypto.com

Para que o robô possa interagir com sua conta na Crypto.com Exchange, você precisará de uma `API Key` e uma `Secret Key`.

1.  **Crie suas chaves de API:**
    *   Faça login na sua conta da Crypto.com Exchange.
    *   Navegue até as configurações da API (geralmente em `Perfil` -> `API Management`).
    *   Crie um novo conjunto de chaves de API, garantindo que as permissões necessárias para trading e consulta de saldo estejam ativadas (por exemplo, `SPOT_TRADE`, `VIEW_BALANCE`).
    *   **Anote sua `API Key` e `Secret Key`. A `Secret Key` é mostrada apenas uma vez!**

2.  **Configure o arquivo `.env`:**
    *   No diretório raiz do projeto (`robofinanceirocripto/`), você encontrará um arquivo `.env`.
    *   Abra este arquivo e preencha suas chaves de API:

    ```
    CRYPTOCOM_API_KEY="SUA_API_KEY_AQUI"
    CRYPTOCOM_SECRET_KEY="SUA_SECRET_KEY_AQUI"
    ```
    *   **Mantenha este arquivo `.env` seguro e nunca o compartilhe publicamente.** Ele já está configurado para ser ignorado pelo Git (`.gitignore`), então suas chaves não serão enviadas para o repositório.

## Uso

O arquivo `bot.py` contém as funções principais para interação com a API. Para executar o robô, ative seu ambiente virtual e execute o script Python:

```bash
source venv/bin/activate
python bot.py
```

As funções de exemplo (como `get_account_summary()`, `place_limit_order()`) estão comentadas no bloco `if __name__ == "__main__":` para evitar execuções acidentais. Descomente e modifique-as conforme suas necessidades para testar as funcionalidades.

### Exemplo de Funções:

*   `get_account_summary()`: Exibe o saldo da sua conta.
*   `get_open_orders('BTC_USDT')`: Lista ordens abertas para o par BTC/USDT.
*   `place_limit_order('BTC_USDT', 'BUY', 60000, 0.0001)`: Coloca uma ordem de compra de limite para 0.0001 BTC a 60000 USDT.
*   `cancel_order('BTC_USDT', 'SEU_ORDER_ID')`: Cancela uma ordem específica.

## Estrutura do Projeto

```
robofinanceirocripto/
├── venv/                 # Ambiente virtual Python
├── .env                  # Variáveis de ambiente (chaves de API)
├── bot.py                # Lógica principal do robô
└── requirements.txt      # Dependências do Python
└── README.md             # Este arquivo de documentação
```

## Desenvolvimento e Personalização (VS Code)

Para um desenvolvimento eficiente no VS Code:

1.  **Abra a pasta do projeto:** No VS Code, vá em `File` > `Open Folder...` e selecione a pasta `robofinanceirocripto`.
2.  **Selecione o interpretador Python:** Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no macOS), digite `Python: Select Interpreter` e escolha o interpretador dentro do seu ambiente virtual (`./venv/bin/python`).
3.  **Extensões Recomendadas:**
    *   **Python** (da Microsoft): Oferece linting, depuração, IntelliSense e muito mais.
    *   **DotEnv** (por `mikestead`): Realça a sintaxe de arquivos `.env`.

Você pode estender este robô para incluir:

*   **Estratégias de Trading:** Implemente lógicas para análise de mercado, indicadores técnicos e tomada de decisão.
*   **Gerenciamento de Risco:** Adicione funcionalidades para stop-loss, take-profit e dimensionamento de posição.
*   **Notificações:** Integre com serviços de notificação (e-mail, Telegram) para alertas sobre operações.
*   **Persistência de Dados:** Armazene o histórico de trades e o estado do robô em um banco de dados.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
