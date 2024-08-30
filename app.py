import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from textblob import TextBlob
import spacy
import pandas as pd
from datetime import datetime
from streamlit_chat import message
import random

# Cargar modelo de lenguaje de spacy
nlp = spacy.load("es_core_news_sm")

st.sidebar.title("Analizador de chats de redes sociales")

uploaded_file = st.sidebar.file_uploader("Selecciona un archivo")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    mydata = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(mydata)

    # Obtener usuarios únicos
    user_list = df['Usuario'].unique().tolist()
    user_list.remove("notificacion_grupal")
    user_list.sort()
    user_list.insert(0, "Todos")

    selected_user = st.sidebar.selectbox("Mostrar análisis con respecto a", user_list)

    # Crear pestañas
    tab1, tab2 = st.tabs(["Análisis", "Mensajes"])

    # Contenido de la pestaña "Análisis"
    with tab1:
        if st.sidebar.button("Mostrar análisis"):
            st.title("Estadísticas principales")
            num_messages, words, num_media_msg, links = helper.fetch_stats(selected_user, df)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("Mensajes totales")
                st.title(num_messages)
            with col2:
                st.header("Palabras totales")
                st.title(words)
            with col3:
                st.header("Elementos multimedia compartidos")
                st.title(num_media_msg)
            with col4:
                st.header("Enlaces compartidos")
                st.title(links)

            # Línea de tiempo mensual
            st.title("Línea de tiempo de actividad mensual")
            timeline = helper.monthly_timeline(selected_user, df)
            fig = px.line(timeline, x='Tiempo', y='Mensaje', title='Línea de tiempo de actividad mensual')
            st.plotly_chart(fig)

            # Línea de tiempo diaria
            st.title("Línea de tiempo de actividad diaria")
            d_timeline = helper.daily_timeline(selected_user, df)
            fig = px.line(d_timeline, x='Fecha', y='Mensaje', title='Línea de tiempo de actividad diaria')
            st.plotly_chart(fig)

            # Mapa de actividad
            st.title("Mapa de actividad")
            col1, col2 = st.columns(2)

            with col1:
                st.header("Día más activo")
                busy_day = helper.week_activity_map(selected_user, df)
                fig = px.bar(busy_day, x=busy_day.index, y=busy_day.values, title='Día más activo')
                st.plotly_chart(fig)

            with col2:
                st.header("Mes más activo")
                busy_month = helper.month_activity_map(selected_user, df)
                fig = px.bar(busy_month, x=busy_month.index, y=busy_month.values, title='Mes más activo')
                st.plotly_chart(fig)

            # Usuarios más activos en el grupo (nivel de grupo)
            if selected_user == 'Todos':
                st.title('Usuarios más activos')
                x, new_df = helper.most_busy_user(df)
                fig = px.bar(x, x=x.index, y=x.values, title='Usuarios más activos')
                st.plotly_chart(fig)
                st.dataframe(new_df.style.highlight_max(color='lightblue')) # Color menos intenso

                # Mapa de calor de actividad semanal
                st.title("Mapa de calor de actividad semanal")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig = px.imshow(user_heatmap,
                               labels=dict(x="Hora del día", y="Día de la semana", color="Nivel de actividad"),
                               x=['00-01', '01-02', '02-03', '03-04', '04-05', '05-06', '06-07', '07-08', '08-09', '09-10',
                                  '10-11',
                                  '11-12', '12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19', '19-20', '20-21',
                                  '21-22', '22-23', '23-00'],
                               y=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
                fig.update_layout(title='Mapa de calor de actividad semanal')
                st.plotly_chart(fig)

            # Nube de palabras
            st.title("Nube de palabras para palabras frecuentes")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # Palabras más comunes
            most_common_df = helper.most_common_words(selected_user, df)
            fig = px.bar(most_common_df, x='Palabras', y='Frecuencia', title='Palabras más comunes')
            st.plotly_chart(fig)

            # Análisis de emojis
            emoji_df = helper.emoji_helper(selected_user, df)
            st.title("Análisis de emojis")
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig = px.pie(emoji_df, values='Frecuencia', names='Emoji', title='Emojis más utilizados')
                st.plotly_chart(fig)

            # Análisis de sentimiento del usuario
            st.title("Análisis de sentimiento")
            user_sentiments = helper.analyze_sentiment(selected_user, df)

            if selected_user == 'Todos':
                overall_sentiment = {key: sum([user[key] for user in user_sentiments.values()]) / len(user_sentiments) for
                                     key
                                     in ['pos', 'neu', 'neg', 'compound']}
                st.subheader("Sentimiento general")

                # Crear un DataFrame de Pandas con las claves como índice
                overall_sentiment_df = pd.DataFrame.from_dict(overall_sentiment, orient='index', columns=['Puntuación'])

                # Renombrar el índice para que sea más descriptivo
                overall_sentiment_df.index = ['Positivo', 'Neutral', 'Negativo', 'Compuesto'] 

                # Crear el gráfico de barras con el DataFrame
                fig = px.bar(overall_sentiment_df, x=overall_sentiment_df.index, y='Puntuación',
                             title='Puntuaciones de sentimiento general',
                             color='Puntuación',
                             color_continuous_scale=['red', 'yellow', 'green'])
                st.plotly_chart(fig)
            else:
                if selected_user in user_sentiments:
                    sentiment_scores = user_sentiments[selected_user]
                    st.subheader(f"Usuario: {selected_user}")

                    # Crear un DataFrame de Pandas con las claves como índice
                    sentiment_scores_df = pd.DataFrame.from_dict(sentiment_scores, orient='index', columns=['Puntuación'])

                    # Renombrar el índice para que sea más descriptivo
                    sentiment_scores_df.index = ['Positivo', 'Neutral', 'Negativo', 'Compuesto']

                    # Crear el gráfico de barras con el DataFrame
                    fig = px.bar(sentiment_scores_df, x=sentiment_scores_df.index, y='Puntuación',
                                 title=f'Puntuaciones de sentimiento para {selected_user}',
                                 color='Puntuación',
                                 color_continuous_scale=['red', 'yellow', 'green'])
                    st.plotly_chart(fig)
                else:
                    st.write(f"No hay resultados de análisis de sentimiento para {selected_user}")

            # Resultados finales del análisis de sentimiento
            sentiment = helper.sentiment_score(user_sentiments, selected_user)
            st.subheader(f"El sentimiento de {selected_user} es {sentiment}")

            # Análisis de entidades nombradas
            st.title("Análisis de entidades nombradas")
            if selected_user == "Todos":
                st.write("Selecciona un usuario específico para ver el análisis de entidades nombradas.")
            else:
                entities = helper.analyze_entities(selected_user, df)
                st.write(f"Entidades nombradas encontradas en los mensajes de {selected_user}:")
                for entity in entities:
                    st.write(f"- {entity.text} ({entity.label_})")


    # Contenido de la pestaña "Mensajes"
    with tab2:
        st.title("Mensajes")

        # Buscador de mensajes
        search_query = st.text_input("Buscar mensajes")

        # Paginación: Inicializar el índice de página
        if "page_number" not in st.session_state:
            st.session_state.page_number = 0

        page_number = st.session_state.page_number
        messages_per_page = 20

        # Filtrar mensajes por búsqueda
        if search_query:
            filtered_df = df[df['Mensaje'].str.contains(search_query, case=False)]
        else:
            filtered_df = df

        # Calcular el índice de inicio y fin para la página actual
        start_index = page_number * messages_per_page
        end_index = start_index + messages_per_page

        # Mostrar los mensajes para la página actual
        for i, row in filtered_df.iloc[start_index:end_index].iterrows():
            # Personalizar el ícono del perfil con inicial aleatoria
            initials = row['Usuario'][0].upper()
            icon = f"{initials}"

            # Añadir un identificador único para evitar el error de claves duplicadas
            unique_key = f"message_{i}"

            # Obtener la hora y la fecha del mensaje
            message_time = row['Fecha'].strftime("%H:%M")
            message_date = row['Fecha'].strftime("%d/%m/%Y")

            # Mostrar el mensaje con la hora y la fecha
            message(row['Mensaje'], is_user=row['Usuario'] == selected_user, avatar_style="initials", seed=icon, key=unique_key)
            st.write(f"<span style='font-size: 10px; color: gray;'>{message_time} - {message_date}</span>", unsafe_allow_html=True)

        # Botones de paginación
        if page_number > 0:
            if st.button("Página anterior"):
                st.session_state.page_number -= 1
                st.rerun()  # Cambiado a st.rerun()

        if end_index < len(filtered_df):
            if st.button("Página siguiente"):
                st.session_state.page_number += 1
                st.rerun()  # Cambiado a st.rerun()