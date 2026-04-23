import google.generativeai as genai
import wikipediaapi
import random
import datetime
import firebase_admin
from firebase_admin import credentials, db
import os
import json

# 1. Настройка времени
now = datetime.datetime.now()
months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
          'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
current_date_for_wiki = f"{now.day}_{months[now.month-1]}"

# 2. Ключи (мы их спрячем в секреты GitHub позже)
api_key = os.getenv("GEMINI_KEY")
firebase_config = os.getenv("FIREBASE_KEY")

genai.configure(api_key=api_key)

# 3. Подключаем Firebase через секретный ключ
if not firebase_admin._apps:
    key_dict = json.loads(firebase_config)
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://vibehistory-d7479-default-rtdb.firebaseio.com/' # <--- ВСТАВЬ СВОЮ ССЫЛКУ ТУТ!
    })

# 4. Логика Википедии и AI
model = genai.GenerativeModel('models/gemma-4-26b-a4b-it')
wiki = wikipediaapi.Wikipedia(user_agent='VibeBot/1.0', language='ru')

try:
    page = wiki.page(current_date_for_wiki)
    events = [e for e in page.section_by_title('События').text.split('\n') if len(e) > 30]
    event = random.choice(events)

    prompt = f"Расскажи об одном интересном историческом событии, которое произошло сегодня. Напиши это в стиле крутого поста для соцсетей, используй эмодзи. Не пиши никаких пояснений, только сам факт. И квиз для этого события: {event}"
    response = model.generate_content(prompt)
    
    db.reference('daily_fact').set({
        'content': response.text,
        'date': current_date_for_wiki
    })
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
