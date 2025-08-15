# Google Maps Scraper

Uma aplicação Flask para fazer scraping de dados do Google Maps de forma automatizada.

## 🚀 Funcionalidades

- Busca automática de empresas no Google Maps
- Extração de informações detalhadas (nome, endereço, telefone, website, avaliações)
- Interface web moderna e responsiva
- Exportação de dados em CSV
- Design limpo com fundo quase branco

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask, Python
- **Scraping**: Selenium, BeautifulSoup4
- **Frontend**: HTML, CSS, JavaScript
- **Banco de Dados**: SQLite
- **Deployment**: Gunicorn

## 📦 Instalação Local

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd google-maps-scraper
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python app.py
```

4. Acesse: `http://localhost:5000`

## 🌐 Deploy em Produção

### Heroku

1. Instale o Heroku CLI
2. Faça login: `heroku login`
3. Crie uma nova app: `heroku create sua-app`
4. Configure os buildpacks:
```bash
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-chromedriver
heroku buildpacks:add --index 3 heroku/python
```
5. Deploy: `git push heroku main`

### Render

1. Conecte seu repositório GitHub ao Render
2. Configure as variáveis de ambiente:
   - `GOOGLE_CHROME_BIN`: `/opt/render/project/.chrome/chrome`
   - `PYTHON_VERSION`: `3.9.16`
3. Use o comando de build: `pip install -r requirements.txt`
4. Use o comando de start: `gunicorn app:app`

### Outras Plataformas

O código foi otimizado para detectar automaticamente diferentes ambientes de deployment e configurar o Chrome adequadamente.

## 🔧 Configuração do Chrome

O aplicativo detecta automaticamente o ambiente e configura o Chrome:

- **Local**: Usa Chrome instalado localmente
- **Heroku**: Usa buildpacks específicos
- **Render**: Usa Chrome pré-instalado
- **Outros**: Fallback para configuração básica

## 📁 Estrutura do Projeto

```
├── app.py                 # Arquivo principal
├── Procfile              # Configuração Heroku
├── requirements.txt      # Dependências Python
├── render.yaml          # Configuração Render
├── app.json             # Configuração Heroku
├── build.sh             # Script de build
└── src/
    ├── main.py          # Aplicação Flask
    ├── routes/          # Rotas da API
    ├── models/          # Modelos de dados
    ├── static/          # Arquivos estáticos
    └── database/        # Banco de dados
```

## 🎨 Interface

- Design moderno com fundo quase branco (#fafafa)
- Interface responsiva e intuitiva
- Tabelas com cabeçalhos em cinza claro
- Botões com gradientes coloridos mantidos

## ⚠️ Considerações Importantes

1. **Rate Limiting**: O Google Maps pode bloquear muitas requisições
2. **Chrome em Produção**: Certifique-se de que o Chrome está disponível
3. **Recursos**: Scraping pode consumir muitos recursos
4. **Termos de Uso**: Respeite os termos de uso do Google

## 🐛 Solução de Problemas

### Chrome não encontrado
- Verifique se os buildpacks estão configurados corretamente
- Confirme as variáveis de ambiente

### Timeout errors
- Aumente o timeout nas configurações
- Reduza o número de resultados por busca

### Memory errors
- Use instâncias com mais memória
- Implemente limpeza de memória

## 📄 Licença

Este projeto está sob a licença MIT.

## 🤝 Contribuição

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.