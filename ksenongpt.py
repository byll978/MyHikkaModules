from .. import loader, utils
import aiohttp
import io
import inspect
import gdown
import os
import requests
from bs4 import BeautifulSoup

# meta developer: @MeKsenon

version = (1, 1, 0)
# changelog: Добавлен поиск в Google

@loader.tds
class KsenonGPTMod(loader.Module):
    """🤖 Модуль для работы с KsenonGPT, генерации изображений и поиска в Google"""

    strings = {"name": "KsenonGPT"}

    async def client_ready(self, client, db):
        self.client = client
        self.github_token = await self.get_github_token()

    async def get_github_token(self):
        token_file = "github_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                return f.read().strip()
        else:
            url = "https://drive.google.com/file/d/14ZyWbeOX5qKBiBAwaxQzuJpJKQ5nChM2/view?usp=drivesdk"
            file_id = url.split("/")[-2]
            download_url = f"https://drive.google.com/uc?id={file_id}"
            try:
                gdown.download(download_url, output=token_file, quiet=False)
                with open(token_file, "r") as f:
                    token = f.read().strip()
                return token
            except Exception as e:
                self.log.error(f"Ошибка при загрузке токена GitHub: {e}")
                return None

    @loader.command()
    async def gpt(self, message):
        """💬 Запрос к GPT с Интернетом. gpt <запрос>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Укажите запрос для GPT.</b>")
            return

        await utils.answer(message, '<emoji document_id=5443038326535759644>💬</emoji> <b>Генерирую ответ на ваш запрос...</b>')

        url = "http://theksenon.pro/api/gpt/generate"
        headers = {"Content-Type": "application/json"}
        prompt = f"{args}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json={"prompt": prompt}) as response:
                    response.raise_for_status()
                    gpt_response = await response.text()
                    gpt_response = gpt_response.encode().decode('unicode-escape').replace('{"response":"', '').rstrip('}')

            await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>Запрос:</b> <i>{args}</i>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{gpt_response}</b>')

        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла ошибка при получении ответа от GPT: {str(e)}</b>")

    @loader.command()
    async def flux(self, message):
        """🎨 Сгенерировать фото, модель flux-pro. .flux <prompt>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Пожалуйста, укажите запрос для генерации изображения. </b>")
            return

        await utils.answer(message, f'<emoji document_id=5431456208487716895>🎨</emoji> <b>Генерирую изображение по запросу </b><i>"{args}"</i>')

        url = "http://theksenon.pro/api/flux/generate"
        headers = {"Content-Type": "application/json"}
        data = {"prompt": args}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    response.raise_for_status()
                    image_url = await response.text()

                async with session.get(image_url) as image_response:
                    image_response.raise_for_status()
                    image_content = io.BytesIO(await image_response.read())

            await message.delete()
            await self.client.send_file(
                message.chat_id,
                image_content,
                caption=f'<emoji document_id=5431456208487716895>🎨</emoji> <b>Изображение по запросу:</b> <i>"{args}"</i>',
                reply_to=message.reply_to_msg_id
            )
        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла ошибка при генерации изображения: {str(e)}</b>")

    @loader.command()
    async def google(self, message):
        """🔎 Поиск в Google. .google <запрос>"""
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Укажите запрос для поиска в Google.</b>")
            return

        await utils.answer(message, "<emoji document_id=5188311512791393083>🔎</emoji><b>Ищу информацию в Google...</b>")

        url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            search_results = soup.find_all("div", class_="g")

            if not search_results:
                await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Результаты поиска не найдены.</b>")
                return

            result_text = "┏ <emoji document_id=5188311512791393083>🔎</emoji> <b>Результаты поиска в Google:</b>\n┃\n"

            for i, result in enumerate(search_results[:3], 1):
                title = result.find("h3")
                description = result.find("div", class_="VwiC3b")
                link = result.find("a")

                if title and description and link:
                    result_text += f"┣ {i}️⃣ <b>{title.text}</b>\n"
                    result_text += f"┣ 📑 <i>Описание: {description.text.strip()}</i>\n"
                    result_text += f"┣ 🌐 URL: <a href='{link['href']}'>Ссылка</a>\n"
                else:
                    result_text += f"┣ {i}️⃣ Не удалось извлечь полную информацию для этого результата.\n"
                
                if i < 3:
                    result_text += "┃\n"

            result_text += "┃\n"
            result_text += "┗ <emoji document_id=5427009714745517609>✅</emoji> KsenonGPT"

            await utils.answer(message, result_text)

        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла ошибка при поиске в Google: {str(e)}</b>")
