# Usa uma imagem do Python leve
FROM python:3.12-slim

# Define o shell padrão
SHELL ["/bin/bash", "-c"]

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . /app

# Instala pacotes do sistema necessários para o Streamlit e Pandas
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Streamlit (ou da sua aplicação)
EXPOSE 8501

# Executa a aplicação
CMD ["streamlit", "run", "Simulador.py", "--server.port=8501", "--server.address=0.0.0.0"]