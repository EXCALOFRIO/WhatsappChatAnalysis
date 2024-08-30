import pandas as pd
import re


def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'Mensaje_usuario': messages, 'Fecha_mensaje': dates})
    df['Fecha_mensaje'] = pd.to_datetime(df['Fecha_mensaje'], format='%d/%m/%y, %H:%M - ')
    df.rename(columns={'Fecha_mensaje': 'Fecha'}, inplace=True)
    users = []
    messages = []
    for message in df['Mensaje_usuario']:
        entry = re.split('([\w\W]+?):\s', message, 1)  # Agregar argumento maxsplit
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('notificacion_grupal')
            messages.append(entry[0])
    df['Usuario'] = users
    df['Mensaje'] = messages
    df.drop(columns=['Mensaje_usuario'], inplace=True)
    df['Año'] = df['Fecha'].dt.year
    df['Mes'] = df['Fecha'].dt.month_name()
    df['Hora'] = df['Fecha'].dt.hour
    df['Minuto'] = df['Fecha'].dt.minute
    df['Mes_num'] = df['Fecha'].dt.month
    # Crear nueva columna para la fecha en formato de solo fecha
    df['Fecha_sola'] = df['Fecha'].dt.date
    df['Dia_semana'] = df['Fecha'].dt.day_name()
    period = []
    for hour in df[['Dia_semana', 'Hora']]['Hora']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['Periodo'] = period
    return df