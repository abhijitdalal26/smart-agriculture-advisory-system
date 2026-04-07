import requests

API_KEY = "606fda0c5bc4a0fc1477de659f256b12"

url = f"https://api.openweathermap.org/data/2.5/weather?lat=19.07&lon=72.87&appid={API_KEY}&units=metric"

response = requests.get(url)
data = response.json()

print(data)