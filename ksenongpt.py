from .. import loader, utils
import requests
import io

# meta developer: Ksenon | @MeKsenon

__version__ = (1, 0, 0)
changelog = "тест"

@loader.tds
class KsenonGPTMod(loader.Module):
    """🤖 Модуль для работы с KsenonGPT и генерации изображений"""

    strings = {"name": "KsenonGPT"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def gpt(self, message):
        """💬 Запрос к GPT с Интернетом. gpt <запрос>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Укажите запрос для GPT.</b>")
            return

        await utils.answer(
            message,
            '<emoji document_id=5443038326535759644>💬</emoji> <b>Генерирую ответ на ваш запрос...</b>'
        )

        url = "http://theksenon.pro/api/gpt/generate"
        headers = {"Content-Type": "application/json"}
        prompt = f"{args}"

        try:
            response = requests.post(url, headers=headers, json={"prompt": prompt})
            response.raise_for_status()
            gpt_response = response.text.strip()
            gpt_response = gpt_response.encode().decode('unicode-escape').replace('{"response":"', '').rstrip('}')

            await utils.answer(
                message,
                f'<emoji document_id=5443038326535759644>💬</emoji> <b>Запрос:</b> <i>{args}</i>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{gpt_response}</b>'
            )

        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Произошла ошибка при получении ответа от GPT: {str(e)}</b>")

    @loader.command()
    async def flux(self, message):
        """🎨 Сгенерировать фото, модель flux-pro. .flux <prompt>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji><b> Пожалуйста, укажите запрос для генерации изображения. </b>")
            return

        await utils.answer(
            message,
            f'<emoji document_id=5431456208487716895>🎨</emoji> <b>Генерирую изображение по запросу </b><i>"{args}"</i>'
        )

        url = "http://theksenon.pro/api/flux/generate"
        headers = {"Content-Type": "application/json"}
        data = {"prompt": args}

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            image_url = response.text.strip()

            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_content = io.BytesIO(image_response.content)

            await message.delete()
            await self.client.send_file(
                message.chat_id,
                image_content,
                caption=(
                    "┏ <emoji document_id=5372981976804366741>🤖</emoji> <b>Изображение успешно создано!</b>\n"
                    "┃\n"
                    f"┣ <emoji document_id=5431456208487716895>🎨</emoji> <b>Запрос:</b> <i>{args}</i>\n"
                    "┃\n"
                    "┣ <emoji document_id=5447410659077661506>🌐</emoji> <b>Модель:</b> <i>flux-pro</i>\n"
                    "┃\n"
                    f"┗ <emoji document_id=5427009714745517609>✅</emoji> <b>Ссылка:</b> <a href='{image_url}'>Изображение</a>"
                )
            )
        except Exception as e:
            await utils.answer(message, f"❌ Произошла ошибка при генерации изображения: {str(e)}")
