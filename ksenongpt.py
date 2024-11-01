from .. import loader, utils
import requests
import io
import aiohttp
import inspect

# meta developer: Ksenon | MeKsenon

version = (1, 0, 3)
# changelog: amogusобработка ошибок в команде flux

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
        except requests.RequestException as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Ошибка при генерации изображения: {str(e)}</b>")
        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Неизвестная ошибка: {str(e)}</b>")

    @loader.command()
    async def kupdate(self, message):
        """- Проверить обновления модуля."""
        module_name = "KsenonGPT"
        module = self.lookup(module_name)
        sys_module = inspect.getmodule(module)

        local_version = sys_module.version
        local_version_str = ".".join(map(str, local_version))

        async with aiohttp.ClientSession() as session:
            async with session.get("https://raw.githubusercontent.com/TheKsenon/MyHikkaModules/refs/heads/main/ksenongpt.py") as response:
                if response.status == 200:
                    remote_content = await response.text()
                    remote_lines = remote_content.splitlines()

                    new_version = tuple(map(int, remote_lines[0].split("=", 1)[1].strip().strip("()").replace(",", "").split()))
                    new_version_str = ".".join(map(str, new_version))

                    changelog = next((line.split(":", 1)[1].strip() for line in remote_lines if line.startswith("# changelog:")), "Нет информации")

                    if new_version > local_version:
                        await utils.answer(message, 
                            f"<emoji document_id=5420323339723881652>⚠️</emoji> <b>У вас старая версия KsenonGPT!</b>\n\n"
                            f"<emoji document_id=5449683594425410231>🔼</emoji> <b>Новая версия: {new_version_str}</b>\n"
                            f"<emoji document_id=5447183459602669338>🔽</emoji> <b>У вас версия: {local_version_str}</b>\n\n"
                            f"<emoji document_id=5447410659077661506>🌐</emoji> <b>Change-log:</b>\n"
                            f"<emoji document_id=5458603043203327669>🔔</emoji> <i>{changelog}</i>\n\n"
                            f"<emoji document_id=5206607081334906820>✔️</emoji> <b>Команда для обновления:</b>\n"
                            f"<code>.dlmod https://raw.githubusercontent.com/TheKsenon/MyHikkaModules/refs/heads/main/ksenongpt.py</code>"
                        )
                    else:
                        await utils.answer(message,
                            f"<emoji document_id=5370870691140737817>🥳</emoji> <b>У вас последняя версия KsenonGPT!</b>\n\n"
                            f"<emoji document_id=5447644880824181073>⚠️</emoji><b> Разработчик модуля почти каждый день делают обновления и баг фиксы, так что часто проверяйте!</b>"
                        )
                else:
                    await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji><b> Не удалось проверить обновления. Попробуйте позже.</b>")
