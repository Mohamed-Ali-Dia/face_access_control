# Utiliser une image Python légère compatible avec dlib/face-recognition
FROM python:3.11-slim

# Mettre à jour le système et installer les dépendances nécessaires pour dlib, OpenCV, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Mettre à jour pip et installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source
COPY . .

# Exposer le port Streamlit
EXPOSE 8501

# Commande pour lancer l'application Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
