#!/bin/bash

# Script de build para deployment
echo "Iniciando build..."

# Instalar dependências Python
pip install -r requirements.txt

# Verificar se estamos em um ambiente de produção
if [ "$RENDER" = "true" ] || [ -n "$DYNO" ]; then
    echo "Ambiente de produção detectado"
    
    # Para Render
    if [ "$RENDER" = "true" ]; then
        echo "Configurando Chrome para Render..."
        # O Render tem Chrome pré-instalado em /opt/render/project/.chrome/
        export GOOGLE_CHROME_BIN=/opt/render/project/.chrome/chrome
    fi
    
    # Para Heroku
    if [ -n "$DYNO" ]; then
        echo "Configurando Chrome para Heroku..."
        # Heroku usa buildpacks para Chrome
        export GOOGLE_CHROME_BIN=/app/.chrome-for-testing/chrome-linux64/chrome
    fi
fi

echo "Build concluído!"