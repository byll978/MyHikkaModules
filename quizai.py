# ------------------------------------------------------------
# Module: QuizAI
# Description: Игра-викторина с разными темами и сложностями
# Author: @kmodules
# ------------------------------------------------------------
# Licensed under the GNU AGPLv3
# https:/www.gnu.org/licenses/agpl-3.0.html
# ------------------------------------------------------------
# Author: @MeKsenon
# Commands: .quiz
# scope: hikka_only
# meta banner: https://i.ibb.co/VWYVC7c/1d011a5f-cb9c-4198-97fa-c4227b41c033.jpg
# meta developer: @kmodules
# ------------------------------------------------------------

import asyncio
import json
import random
import requests
from .. import loader, utils
from telethon.tl.types import Message
from telethon.tl.functions.channels import JoinChannelRequest

@loader.tds
class QuizGameMod(loader.Module):
    """Игра-викторина с разными темами и сложностями"""

    strings = {"name": "QuizAI"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "api_key",
            "",
            lambda: "Введите сюда свой API-Key",
        )

    def init(self):
        self.config = loader.ModuleConfig(
            "api_key",
            "",
            lambda: "Возьмите свой API-Key отсюда: https://aistudio.google.com"
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._quiz_data = None
        self._used_questions = set()
        self.correct_answers = 0
        self.total_questions = 0
        await client(JoinChannelRequest("kmodules"))
        
    @loader.command()
    async def quiz(self, message: Message):
        """Начать викторину
        Аргументы: -t "тема" -d <easy/normal/hard>
        Пример: .quiz -t "Minecraft" -d easy"""
        
        if not self.config["api_key"]:
            await utils.answer(message, "❌ Установите API-Key!\nВозьмите свой API-Key отсюда: https://aistudio.google.com\nДалее введите: .fcfg QuizAI api_key КЛЮЧ")
            return
        
        args = utils.get_args_raw(message)
        
        try:
            parts = args.split('" -')
            theme_part = parts[0].split('-t "')[1]
            difficulty = parts[1].split('d ')[1].lower()
        except:
            await utils.answer(message, '❌ Используйте: .quiz -t "тема" -d <сложность>\nПример: .quiz -t "Minecraft" -d easy')
            return
            
        if difficulty not in ["easy", "normal", "hard","extreme"]:
            await utils.answer(message, "❌ Сложность может быть: easy, normal или hard/extreme")
            return
            
        await utils.answer(message, """┏🔄 Генерирую нейро-викторину...
┃
┗ 🔥 Модель: gemini-1.5-pro-0827, будет немного долго.""")
        
        system_prompt = f'''You are a quiz generator. Generate 10 very accurate and specific questions about {theme_part}.

Rules:
1. Questions must be specifically about {theme_part}
2. All answers must be factually correct
3. Wrong answers must be plausible but clearly incorrect
4. Questions difficulty should match {difficulty} level
5. No duplicates or similar questions
6. Questions should test real knowledge about {theme_part}

Return exactly this JSON format:
{{
  "quiz": {{
    "quiz_1": {{
      "question": "your specific question",
      "quiz_theme": "{theme_part}",
      "difficulty": "{difficulty}",
      "answer": "correct answer",
      "not_correct_answers": [
        "wrong answer 1",
        "wrong answer 2", 
        "wrong answer 3"
      ]
    }},
    "quiz_2": {{...}},
    ...up to quiz_10
  }}
}}

Return ONLY valid JSON, no other text. Default: Russian language. Generate on russian language, if no on this language...'''
        
        result = self.gemini_request(system_prompt)
        if not result:
             await utils.answer(message, "😔 Ошибка при получении данных от API. Проверьте API-Key и повторите попытку.")
             return
        try:
            self._quiz_data = json.loads(result)
        except json.JSONDecodeError:
             await utils.answer(message, "😔 Ошибка при обработке данных от API. Проверьте ответ от API.")
             return
        self._used_questions = set()
        self.correct_answers = 0
        self.total_questions = 0
        
        await self.show_question(message)
        
    async def get_unused_question(self):
        available_questions = [q for q in self._quiz_data["quiz"].values() 
                             if q["question"] not in self._used_questions]
            
        if not available_questions:
            return None
        
        question = random.choice(available_questions)
        self._used_questions.add(question["question"])
        return question
        
    async def show_question(self, message):
        current_quiz = await self.get_unused_question()
        
        if not current_quiz:
            await utils.answer(message, "😔 Закончились вопросы.")
            return
        
        answers = current_quiz["not_correct_answers"] + [current_quiz["answer"]]
        random.shuffle(answers)
        
        buttons = []
        for answer in answers:
            buttons.append([{
                "text": answer,
                "callback": self.quiz_callback,
                "args": (answer == current_quiz["answer"], current_quiz)
            }])
            
        await self.inline.form(
            text=f"""┏ ❓ Вопрос: {current_quiz["question"]}
┣ 📑 Сложность: {current_quiz["difficulty"]}
┣ 📊 Прогресс: {self.total_questions}/10
┗ ⚙️ Ответы:""",
            message=message,
            reply_markup=buttons
        )
    
    async def quiz_callback(self, call, is_correct: bool, current_quiz: dict):
        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1
            
        if self.total_questions >= 10:
            accuracy = (self.correct_answers / 10) * 100
            await call.edit(
                text=f"""┏ 🎯 Викторина завершена!
┃
┣ 📊 Ваша статистика:
┣ ✅ Правильных ответов: {self.correct_answers}
┣ ❌ Неправильных ответов: {10 - self.correct_answers}
┣ 📈 Точность: {accuracy:.1f}%
┃
┗ 🔄 Новая игра: .quiz"""
            )
            return
            
        next_quiz = await self.get_unused_question()
        if not next_quiz:
            await call.edit(
                text=f"""😔 Закончились вопросы.
┏ 🎯 Викторина завершена!
┃
┣ 📊 Ваша статистика:
┣ ✅ Правильных ответов: {self.correct_answers}
┣ ❌ Неправильных ответов: {10 - self.correct_answers}
┣ 📈 Точность: {accuracy:.1f}%
┃
┗ 🔄 Новая игра: .quiz"""
            )
            return
        answers = next_quiz["not_correct_answers"] + [next_quiz["answer"]]
        random.shuffle(answers)
        
        buttons = []
        for answer in answers:
            buttons.append([{
                "text": answer,
                "callback": self.quiz_callback,
                "args": (answer == next_quiz["answer"], next_quiz)
            }])

        if is_correct:
            text = f"""┏ ✅ Правильно!
┗ Ответ: {current_quiz["answer"]}

┏ ❓ Вопрос: {next_quiz["question"]}
┣ 📑 Сложность: {next_quiz["difficulty"]}
┣ 📊 Прогресс: {self.total_questions}/10
┗ ⚙️ Ответы:"""
        else:
            text = f"""┏ ❌ Неправильно!
┗ Правильный ответ: {current_quiz["answer"]}

┏ ❓ Вопрос: {next_quiz["question"]}
┣ 📑 Сложность: {next_quiz["difficulty"]}
┣ 📊 Прогресс: {self.total_questions}/10
┗ ⚙️ Ответы:"""
            
        await call.edit(
            text=text,
            reply_markup=buttons
        )
    
    def gemini_request(self, prompt):
        GEMINI_API_KEY = self.config["api_key"]
        BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-exp-0827:generateContent"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts":[
                    {"text": prompt}
                ]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "candidateCount": 1
            }
        }

        proxies = {
            'http': 'http://nkzeuopd:od0ij6ste4xi@107.172.163.27:6543',
            'https': 'http://nkzeuopd:od0ij6ste4xi@107.172.163.27:6543'
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=data,
                proxies=proxies,
                verify=False,
                timeout=80
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException as e:
            return None
        except (KeyError, json.JSONDecodeError):
            return None
