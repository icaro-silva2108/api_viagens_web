# :pencil2: Descrição
API REST para gerenciamento de usuários, reservas e destinos, com foco em autenticação, segurança e testes.  
O projeto conta com funcionalidades como:
- Cadastro de Usuários  
- Login e Autenticação  
- Cancelamento de Cadastro e Atualização de Informações  
- Listagem, Criação e Cancelamento de Reservas   
- Listagem de destinos

# :iphone: Tecnologias Utilizadas:
- Python  
- MySQL  
- Flask  
- Pytest

# :bookmark_tabs: Estrutura do Projeto
- app/  
    - database/: Scripts SQL e conexão com o banco  
    - api/: Rotas, JWTmanager e rate limiter  
    - tests/: Testes  
    - services/: Regras de negócio, utilities e security(para hasheamento de senhas)

# :chart_with_upwards_trend: Objetivo do Projeto
O objetivo do projeto é aprofundar conhecimentos de desenvolvimento backend/web e estruturação de APIs REST, conexão com banco de dados relacional, autenticação via JWT, testes de software e controle de acesso a rotas protegidas. Inicialmente o projeto foi planejado como fullstack, mas por meio de uma decisão foi reestruturado para o foco exclusivo em backend, visando aprofundamento técnico e boas práticas.

# :hourglass: Próximos Passos
- Finalizar testes automatizados.  
- Atualizar documentação ao longo do projeto.  

# :computer: Como Rodar o Projeto Localmente

## :page_facing_up: 1. Requisitos iniciais:

- Tenha instalado o Python com versão maior ou igual a 3.9+(Recomendação: 3.11.9 - Usada para o desenvolvimento)  
- Escolha uma pasta que deseja alocar o projeto(opcional).
- Tenha o MySQL instalado e em execução.

## :inbox_tray: 2. Clone o Repositório:

- Abra o Git Bash em uma pasta de sua preferência.  
- Dentro do terminal Git use:  
```bash
git clone https://github.com/icaro-silva2108/api_viagens_web.git
```
- Acesse a pasta criada:  
```console
cd api_viagens_web
```

## :wrench: 3. Configuração de Ambiente:

- Dentro da pasta do projeto inicie o ambiente virtual através do terminal:  
```console
python -m venv venv
```  
- Ative o ambiente virtual com:  
```console
venv\Scripts\Activate
```  
- Obs: Certifique-se de que aparece "(venv)" antes do caminho no terminal.

## :file_folder: 4. Instalar Dependências(Libs):

- Use o arquivo requirements.txt para instalar as Libs externas:  
```console
pip install -r requirements.txt
```

## :game_die: 5. Configurar Database:

- Usando o MySQL, crie um Schema que será conectado ao projeto.
```sql
CREATE DATABASE api_viagens;
```
- Use os scripts para criar as tabelas em localizados em:  
app/database/tables.sql  
app/database/destinations_seed.sql  
app/database/token_blacklist.sql

## :recycle: 6. Configure o .env:

- Adicione um arquivo .env no projeto.  
- Para definir as variáveis de ambiente necessárias, use o arquivo .env.example do repositório como referência. Ou faça como no exemplo:
```env
DB_HOST=localhost
DB_USER=seu_usuário
DB_PASSWORD=sua_senha
DB_NAME=seu_database
JWT_SECRET_KEY=sua_chave_secreta
```

## :microscope: 7. Executar e Testar a API:

- Com o ambiente virtual ativado, execute:  
```console
python -m main
```
- A rota do servidor deve aparecer em algo como:  
```console
Running on http://127.0.0.1:5000
```

### Para testar você pode usar as seguintes ferramentas:

- Postman
- Insomnia
- Thunder Client(VS Code)

Exemplo(Rota pública, não precisa de autenticação):
```console
GET http://127.0.0.1:5000/api/destinations
```

A resposta deve ser:  
```JSON
{
  "destinations": [
    {
      "city": "Paris",
      "country": "França",
      "description": "Conheça a Torre Eiffel, museus e a cultura francesa.",
      "id": 2,
      "img_url": null,
      "price": 4500.0
    },
    {
      "city": "Nova York",
      "country": "Estados Unidos",
      "description": "Explore a Times Square, Central Park e Broadway.",
      "id": 3,
      "img_url": null,
      "price": 5200.0
    },
    {
      "city": "Tóquio",
      "country": "Japão",
      "description": "Tecnologia, tradição e gastronomia japonesa.",
      "id": 4,
      "img_url": null,
      "price": 6100.0
    },
    {
      "city": "Rio de Janeiro",
      "country": "Brasil",
      "description": "Praias, Cristo Redentor e vida cultural intensa.",
      "id": 5,
      "img_url": null,
      "price": 2800.0
    },
    {
      "city": "Roma",
      "country": "Itália",
      "description": "História, Coliseu e culinária italiana.",
      "id": 6,
      "img_url": null,
      "price": 4300.0
    }
  ],
  "success": true
}
```
