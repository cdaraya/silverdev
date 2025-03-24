# Usar una imagen base oficial de Python
FROM python:3.13.2

# Establecer el directorio de trabajo en el contenedor
WORKDIR /usr/src/app

# Copiar el archivo requirements.txt
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de tu código fuente al contenedor
COPY . .

# Comando a ejecutar cuando se inicie el contenedor
CMD ["python", "./Prov_Factoring_SQL.py"]  # Cambia 'Prov_Factoring_SQL.py' por el nombre de tu script principal
