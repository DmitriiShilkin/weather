import aiohttp

from .constants import WEATHER_CODES, WIND_DIRECTION_CODES


async def get_weather(latitude, longitude):
    async with aiohttp.ClientSession() as session:
        # команда для отправки запроса к API
        url = 'https://api.open-meteo.com/v1/forecast'
        # задаем параметры передачи запроса
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'timezone': 'auto',
            'current': 'temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_direction_10m,\
weather_code',
            'daily': 'temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,\
wind_speed_10m_max,wind_direction_10m_dominant,weather_code'
        }
        async with session.get(url, params=params) as response:
            weather_json = await response.json()

    return weather_json


def get_context_data(data):
    context_data = []
    current_data = data['current']
    daily_data = data["daily"]
    days = len(daily_data['time'])

    context_data.append("Текущая погода:")
    context_data.append(WEATHER_CODES[current_data['weather_code']])
    context_data.append(
        f"Температура(ощущается): {current_data['temperature_2m']}"
        f"({current_data['apparent_temperature']})°C"
    )
    context_data.append(
        f"Относительная влажность: {current_data['relative_humidity_2m']}%"
    )
    context_data.append(
        f"Скорость ветра: {round(current_data['wind_speed_10m'] * 10 / 36, 1)} м/с"
    )
    context_data.append(
        f"Направление ветра: {WIND_DIRECTION_CODES[current_data['wind_direction_10m']]}"
    )
    context_data.append(" ")
    context_data.append(f"Прогноз на ближайшие {days} дней:")

    for i in range(days):
        context_data.append(f"Дата: {daily_data['time'][i]}")
        context_data.append(WEATHER_CODES[daily_data['weather_code'][i]])
        context_data.append(
            f"Температура(ощущается) max: {daily_data['temperature_2m_max'][i]}"
            f"({daily_data['apparent_temperature_max'][i]})°C"
        )
        context_data.append(
            f"Температура(ощущается) min: {daily_data['temperature_2m_min'][i]}"
            f"({daily_data['apparent_temperature_min'][i]})°C"
        )
        context_data.append(
            f"Скорость ветра max: {round(daily_data['wind_speed_10m_max'][i] * 10 / 36, 1)} м/с"
        )
        context_data.append(
            f"Направление ветра преимущественно: "
            f"{WIND_DIRECTION_CODES[daily_data['wind_direction_10m_dominant'][i]]}"
        )
        context_data.append(" ")

    return context_data
