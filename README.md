# Analizador de Chats de WhatsApp

Este proyecto es una aplicación para el análisis de chats de WhatsApp construida con Streamlit. La aplicación permite analizar conversaciones, generar estadísticas y visualizar datos a través de gráficos e informes.

## Requisitos

Antes de ejecutar la aplicación, asegúrate de tener instalados los siguientes requisitos:

- **Python** (versión 3.8 o superior)
- **Pip** (gestor de paquetes de Python)

## Instalación

1. **Clona este repositorio**:

   ```bash
   git clone https://github.com/EXCALOFRIO/WhatsappChatAnalysis.git
   cd analizador-whatsapp

   ```

2. **Crea un entorno virtual (opcional, pero recomendado):**:

   ```bash
   python -m venv venv

   ```

3. **Activa el entorno virtual**:

   - En Windows:
     ```bash
     venv\Scripts\activate
     ```
   - En macOS y Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Instala las dependencias**:

   ```bash
   pip install -r requirements.txt

   ```

5. **Además, necesitarás descargar el modelo de lenguaje de spaCy para español. Puedes hacerlo con el siguiente comando:**
   ```bash
   python -m spacy download es_core_news_md
   ```

## Ejecución

Para ejecutar la aplicación, utiliza el siguiente comando:

```bash
streamlit run app.py
```

## Uso

1. **Sube un archivo**: En el panel lateral, selecciona un archivo de chat de WhatsApp para analizar. El archivo debe estar en formato de texto.

2. **Selecciona un usuario**: En el panel lateral, elige el usuario para el cual deseas realizar el análisis o selecciona "Todos" para un análisis grupal.

3. **Explora las pestañas**: La aplicación tiene dos pestañas principales:

   - **Análisis**: Muestra estadísticas generales, gráficos y análisis de datos.
   - **Mensajes**: Permite buscar y visualizar mensajes individuales.

4. **Filtra y navega**: Utiliza las opciones de filtrado y navegación en la pestaña de mensajes para examinar los chats con detalle.

### Pestaña "Análisis"

- **Estadísticas principales**: Muestra el número total de mensajes, palabras, elementos multimedia compartidos y enlaces compartidos.
- **Líneas de tiempo**: Gráficos que muestran la actividad mensual y diaria.
- **Mapas de actividad**: Visualiza el día y mes más activo.
- **Usuarios más activos**: Muestra los usuarios más activos si se selecciona "Todos".
- **Nube de palabras**: Visualiza las palabras más frecuentes.
- **Análisis de emojis**: Muestra la frecuencia de uso de emojis.
- **Análisis de sentimiento**: Muestra el análisis de sentimiento general y por usuario.
- **Análisis de entidades nombradas**: Extrae y visualiza entidades nombradas en los mensajes.

### Pestaña "Mensajes"

- **Buscador de mensajes**: Filtra mensajes por búsqueda.
- **Paginación**: Navega por los mensajes en páginas con controles de navegación.

## Contribuciones

Si deseas contribuir al proyecto, por favor, realiza un fork del repositorio, haz tus cambios y envía un pull request. Asegúrate de seguir las mejores prácticas y mantener el código limpio.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
