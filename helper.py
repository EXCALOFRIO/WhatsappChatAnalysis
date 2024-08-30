from urlextract import URLExtract
from wordcloud import WordCloud
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
from collections import Counter
import emoji
from textblob import TextBlob
import spacy
import streamlit as st  # Importar streamlit

# Cargar modelo de lenguaje de spacy (una sola vez)
nlp = spacy.load("es_core_news_sm")

extract = URLExtract()

# Descargar el lexicon de VADER solo una vez
nltk.download('vader_lexicon')


def fetch_stats(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]

    # Obtener el número de mensajes
    num_messages = df.shape[0]

    # Obtener el número total de palabras
    words = []
    for messages in df['Mensaje']:
        words.extend(messages.split())

    # Obtener el número de mensajes multimedia
    num_media_msg = df[df['Mensaje'] == '<Multimedia omitido>\n'].shape[0]

    # Obtener el número de enlaces compartidos
    links = []
    for message in df['Mensaje']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_msg, len(links)


# Encontrar los usuarios más activos en el grupo (nivel de grupo)
def most_busy_user(df):
    # Filtrar 'notificacion_grupal'
    df_filtered = df[df['Usuario'] != 'notificacion_grupal']
    x = df_filtered['Usuario'].value_counts().head()
    df_percent = round((df_filtered['Usuario'].value_counts() / df_filtered.shape[0]) * 100, 2).reset_index().rename(
        columns={'Usuario': 'Nombre', 'count': 'Porcentaje'})
    return x, df_percent


def create_wordcloud(selected_user, df):
    f = open('stopwords.txt', 'r', encoding='utf-8')
    stop_words = f.read()

    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]
    temp = df[df['Usuario'] != 'notificacion_grupal']
    temp = temp[temp['Mensaje'] != '<Multimedia omitido>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp["Mensaje"] = temp["Mensaje"].apply(remove_stop_words)
    df_wc = wc.generate(df['Mensaje'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    f = open('stopwords.txt', 'r', encoding='utf-8')
    stop_words = f.read()
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]

    # Convertir mensajes a minúsculas y eliminar espacios en blanco
    df['Mensaje'] = df['Mensaje'].str.lower().str.strip()

    # Filtrar '<multimedia omitido>' y 'notificacion_grupal'
    temp = df[~df['Mensaje'].str.contains('<multimedia omitido>', case=False, na=False)]
    temp = temp[temp['Usuario'] != 'notificacion_grupal']

    words = []
    for message in temp['Mensaje']:
        for word in message.split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20)).rename(columns={0: "Palabras", 1: "Frecuencia"})
    return most_common_df


# Análisis de emojis
def emoji_helper(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]
    emojis = []
    for message in df['Mensaje']:
        emojis.extend([c for c in message if emoji.demojize(c) != c])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis)))).rename(
        columns={0: "Emoji", 1: "Frecuencia"})

    # Devolver solo las 6 primeras filas
    return emoji_df.head(8)


def monthly_timeline(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]
    timeline = df.groupby(['Año', 'Mes_num', 'Mes']).count()['Mensaje'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['Mes'][i] + "-" + str(timeline['Año'][i]))
    timeline['Tiempo'] = time
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]
    daily_timeline = df.groupby('Fecha').count()['Mensaje'].reset_index()
    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]
    return df['Dia_semana'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]
    return df['Mes'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]
    user_heatmap = df.pivot_table(index='Dia_semana', columns='Periodo', values='Mensaje', aggfunc='count').fillna(0)
    return user_heatmap


# Análisis de sentimiento de cada usuario basado en el texto y los emojis utilizados

sia = SentimentIntensityAnalyzer()  # Inicializar fuera de la función para mayor eficiencia


def analyze_sentiment(selected_user, df):
    user_sentiments = {}
    for index, row in df.iterrows():
        user = row['Usuario']
        message = row['Mensaje']
        if user not in user_sentiments:
            user_sentiments[user] = {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0}
        # Analizar el sentimiento del texto
        text_sentiment = sia.polarity_scores(message)
        for key in user_sentiments[user].keys():
            user_sentiments[user][key] += text_sentiment[key]
        # Analizar el sentimiento de los emojis
        emojis = [c for c in message if emoji.demojize(c) != c]
        for emo in emojis:
            emoji_sentiment = {
                '😀': 1.0,  # Sentimiento positivo
                '😢': -1.0,  # Sentimiento negativo
                '😠': -1.0,  # Sentimiento negativo
                '😍': 1.0,  # Sentimiento positivo
                '😐': 0.0,  # Sentimiento neutral
            }
            if emo in emoji_sentiment:
                user_sentiments[user]['compound'] += emoji_sentiment[emo]
    # Promediar las puntuaciones de sentimiento
    for user, sentiment_scores in user_sentiments.items():
        total_messages = df[df['Usuario'] == user].shape[0]
        for key in sentiment_scores.keys():
            sentiment_scores[key] /= total_messages
    if selected_user == 'Todos':
        return user_sentiments
    else:
        return {selected_user: user_sentiments.get(selected_user,
                                                {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0})}


def sentiment_score(user_sentiments, selected_user):
    if selected_user == 'Todos':
        pos = sum([user['pos'] for user in user_sentiments.values()]) / len(user_sentiments)
        neg = sum([user['neg'] for user in user_sentiments.values()]) / len(user_sentiments)
        neu = sum([user['neu'] for user in user_sentiments.values()]) / len(user_sentiments)
    elif selected_user in user_sentiments:
        sentiment_scores = user_sentiments[selected_user]
        pos = sentiment_scores['pos']
        neg = sentiment_scores['neg']
        neu = sentiment_scores['neu']
    else:
        return "No hay resultados de análisis de sentimiento para el usuario seleccionado"
    if (pos > neg) and (pos > neu):
        return "Positivo 😊"
    elif (neg > pos) and (neg > neu):
        return "Negativo 😠"
    else:
        return "Neutral 🙂"


def analyze_entities(selected_user, df):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]

    entities = []
    for message in df['Mensaje']:
        doc = nlp(message)
        for entity in doc.ents:
            entities.append(entity)

    return entities


@st.cache_data  # Reemplazar st.cache por st.cache_data
def load_messages(selected_user, df, batch_size, offset):
    if selected_user != "Todos":
        df = df[df['Usuario'] == selected_user]

    messages = []
    for index, row in df.iloc[offset:offset + batch_size].iterrows():
        messages.append({
            "sender": row['Usuario'],
            "message": row['Mensaje'],
            "timestamp": row['Fecha'].strftime("%I:%M %p"),
            "date": row['Fecha'].date()  # Agregar la fecha
        })

    return messages