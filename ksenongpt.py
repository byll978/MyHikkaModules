from .. import loader, utils
import aiohttp
import io
import inspect
import random
import gdown
import os
import requests
import json
from bs4 import BeautifulSoup

__version__ = (1, 3, 9)
version = __version__ 

# changelog: Добавлена gpt-4-turbo, английский язык, фиксы, обязательно обновитесь 

@loader.tds
class KsenonGPTMod(loader.Module):
    """🤖 Module for working with KsenonGPT and image generation"""

    strings = {
        "name": "KsenonGPT",
        "no_args": "<emoji document_id=5210952531676504517>❌</emoji><b>Please specify a query.</b>",
        "generating": '<emoji document_id=5443038326535759644>💬</emoji> <b>Generating response to your query...</b>',
        "generating_image": '<emoji document_id=5431456208487716895>🎨</emoji> <b>Generating image for query </b><code>"{}"</code>...\n<emoji document_id=5334544901428229844>ℹ️</emoji> <b>Model:</b> <i>{}</i>\n{}',
        "error": "<emoji document_id=5210952531676504517>❌</emoji><b>Error: {}</b>",
        "success_image": "┏ <emoji document_id=5372981976804366741>🤖</emoji> <b>Image successfully created!</b>\n┃\n┣ <emoji document_id=5431456208487716895>🎨</emoji> <b>Query:</b> <code>{}</code>\n┃\n┣ <emoji document_id=5447410659077661506>🌐</emoji> <b>Model:</b> <i>{}</i>\n┃\n┗ <emoji document_id=5427009714745517609>✅</emoji> <b>Link:</b> <a href='{}'>Image</a>",
        "searching": "<emoji document_id=5188311512791393083>🔎</emoji><b>Searching in Google...</b>",
        "no_results": "<emoji document_id=5210952531676504517>❌</emoji><b>No search results found.</b>",
        "update_available": "<emoji document_id=5420323339723881652>⚠️</emoji> <b>KsenonGPT update available!</b>\n\n<emoji document_id=5449683594425410231>🔼</emoji> <b>New version: {}</b>\n<emoji document_id=5447183459602669338>🔽</emoji> <b>Current version: {}</b>\n\n<emoji document_id=5447410659077661506>🌐</emoji> <b>Changelog:</b>\n<emoji document_id=5458603043203327669>🔔</emoji> <i>{}</i>\n\n<emoji document_id=5206607081334906820>✔️</emoji> <b>Update command:</b>\n<code>.dlmod {}</code>",
        "latest_version": "<emoji document_id=5370870691140737817>🥳</emoji> <b>You have the latest version of KsenonGPT!</b>\n\n<emoji document_id=5447644880824181073>⚠️</emoji><b>Developers make updates and bug fixes almost daily, so check often!</b>",
        "ip_blocked": "<emoji document_id=5210952531676504517>❌</emoji> <b>Your IP has been blocked!</b>\n\n<emoji document_id=5395444514028529554>🫦</emoji> <b>IP is only blocked when generating hardcore NSFW + politics.</b>",
        "old_version": "<emoji document_id=5240241223632954241>🚫</emoji> <b>You have an old version of KsenonGPT</b>, <b>you need to update, as the module may not work soon on this version.</b>\n\n<emoji document_id=5467538555158943525>💭</emoji> <b>Use kupdate</b> - <i>command</i>."
    }

    strings_ru = {
        "name": "KsenonGPT",
        "no_args": "<emoji document_id=5210952531676504517>❌</emoji><b>Пожалуйста, укажите запрос.</b>",
        "generating": '<emoji document_id=5443038326535759644>💬</emoji> <b>Генерирую ответ на ваш запрос...</b>',
        "generating_image": '<emoji document_id=5431456208487716895>🎨</emoji> <b>Генерирую изображение по запросу </b><code>"{}"</code>...\n<emoji document_id=5334544901428229844>ℹ️</emoji> <b>Модель:</b> <i>{}</i>\n{}',
        "error": "<emoji document_id=5210952531676504517>❌</emoji><b>Ошибка: {}</b>",
        "success_image": "┏ <emoji document_id=5372981976804366741>🤖</emoji> <b>Изображение успешно создано!</b>\n┃\n┣ <emoji document_id=5431456208487716895>🎨</emoji> <b>Запрос:</b> <code>{}</code>\n┃\n┣ <emoji document_id=5447410659077661506>🌐</emoji> <b>Модель:</b> <i>{}</i>\n┃\n┗ <emoji document_id=5427009714745517609>✅</emoji> <b>Ссылка:</b> <a href='{}'>Изображение</a>",
        "searching": "<emoji document_id=5188311512791393083>🔎</emoji><b>Ищу информацию в Google...</b>",
        "no_results": "<emoji document_id=5210952531676504517>❌</emoji><b>Результаты поиска не найдены.</b>",
        "update_available": "<emoji document_id=5420323339723881652>⚠️</emoji> <b>Доступно обновление KsenonGPT!</b>\n\n<emoji document_id=5449683594425410231>🔼</emoji> <b>Новая версия: {}</b>\n<emoji document_id=5447183459602669338>🔽</emoji> <b>Текущая версия: {}</b>\n\n<emoji document_id=5447410659077661506>🌐</emoji> <b>Список изменений:</b>\n<emoji document_id=5458603043203327669>🔔</emoji> <i>{}</i>\n\n<emoji document_id=5206607081334906820>✔️</emoji> <b>Команда для обновления:</b>\n<code>.dlmod {}</code>",
        "latest_version": "<emoji document_id=5370870691140737817>🥳</emoji> <b>У вас последняя версия KsenonGPT!</b>\n\n<emoji document_id=5447644880824181073>⚠️</emoji><b>Разработчики делают обновления и исправления почти каждый день, проверяйте чаще!</b>",
        "ip_blocked": "<emoji document_id=5210952531676504517>❌</emoji> <b>Ваш IP был заблокирован!</b>\n\n<emoji document_id=5395444514028529554>🫦</emoji> <b>IP блокируется только при генерации жёсткой NSFW + политика.</b>",
        "old_version": "<emoji document_id=5240241223632954241>🚫</emoji> <b>У вас старая версия KsenonGPT</b>, <b>вам нужно обновиться, ведь модуль не может скоро работать на данной версии.</b>\n\n<emoji document_id=5467538555158943525>💭</emoji> <b>Используйте kupdate</b> - <i>команда</i>."
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "VALUE",
                "",
                "TEXT",
                validator=loader.validators.Hidden(loader.validators.String()),
            ),
        )

    async def client_ready(self, client, db):
        self.client = client
        self._db = db
        self.github_token = await self.get_github_token()

    def get_lang(self):
        with open(f'config-{self.tg_id}.json', 'r') as fh:
            data = json.load(fh)
        return data['hikka.translations']['lang']

    async def check_version(self):
        url = "https://raw.githubusercontent.com/TheKsenon/MyHikkaModules/main/ksenongpt.py"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    for line in content.splitlines():
                        if line.startswith("__version__"):
                            remote_version = eval(line.split("=")[1].strip())
                            if remote_version > __version__:
                                return False
        return True

    async def generate_text_with_gpt(self, prompt, model="gpt-3-web"):
        if not await self.check_version():
            return "OLD_VERSION"

        url = "http://theksenon.pro/v1/chat/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a friendly userbot"},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 403:
                try:
                    error_data = response.json()
                    if "error" in error_data and "IP" in error_data["error"]:
                        return "IP_BLOCKED"
                except:
                    pass
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            if "403" in str(e):
                return "IP_BLOCKED"
            return None

    async def generate_phi_text(self, prompt):
        return await self.generate_text_with_gpt(prompt, model="phi-3.5-mini")
        
    async def get_github_token(self):
        token = self._db.get("KsenonGPT", "github_token", None)
        if token:
            return token
        token_file = "github_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                token = f.read().strip()
        else:
            url = "https://drive.google.com/file/d/14ZyWbeOX5qKBiBAwaxQzuJpJKQ5nChM2/view?usp=drivesdk"
            file_id = url.split("/")[-2]
            download_url = f"https://drive.google.com/uc?id={file_id}"
            try:
                gdown.download(download_url, output=token_file, quiet=False)
                with open(token_file, "r") as f:
                    token = f.read().strip()
            except Exception as e:
                return None
        self._db.set("KsenonGPT", "github_token", token)
        return token

    async def generate_image(self, message, args, model):
        hints = [
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Add \"pixel graphic\" to get pixel photo.</b>",
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Add \"4K-hyper realistic\" to get realistic result.</b>",
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Add \"no blur\" to avoid blurring.</b>",
            "<emoji document_id=5224607267797606837>☄️</emoji> <b>Add \"DSC_0123.JPG\" to make it super realistic.</b>",
            ""
        ]
        hint = random.choice(hints)
        display_model = model
        if model == "flux-pro":
            display_model = "flux-pro-mv"
        elif model == "sdxl":
            display_model = "stable-diffusion-3.5-large"
        elif model == "pixart-alpha":
            display_model = "pixart-alpha"

        await utils.answer(message, self.strings['generating_image'].format(args, display_model, hint))

        if model == "flux-pro":
            url = "http://theksenon.pro/api/flux/generate"
        elif model == "sdxl":
            url = "http://theksenon.pro/api/sdxl/generate"
        else:
            url = f"http://api.theksenon.pro/api/{model.split('-')[0]}/generate"

        headers = {"Content-Type": "application/json"}
        data = {"prompt": args}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 403:
                        try:
                            error_data = await response.json()
                            if "error" in error_data and "IP" in error_data["error"]:
                                await utils.answer(message, self.strings['ip_blocked'])
                                return
                        except:
                            pass
                    response.raise_for_status()
                    data = await response.text()
                    try:
                        data = json.loads(data)
                        image_url = data.get("image_url")
                    except json.JSONDecodeError:
                        image_url = data.strip()

                    async with session.get(image_url) as image_response:
                        image_response.raise_for_status()
                        image_content = io.BytesIO(await image_response.read())
            await message.delete()
            await self.client.send_file(
                message.chat_id,
                image_content,
                caption=self.strings['success_image'].format(args, display_model, image_url)
            )
        except aiohttp.ClientResponseError as e:
            if e.status == 403:
                await utils.answer(message, self.strings['ip_blocked'])
            else:
                await utils.answer(message, self.strings['error'].format(f"{e.status}, {e.message}"))
        except Exception as e:
            await utils.answer(message, self.strings['error'].format(str(e)))

    @loader.command(ru_doc="🎨 Сгенерировать фото, модель flux-pro-mv. .flux <prompt>")
    async def flux(self, message):
        """🎨 Generate image using flux-pro-mv model. Usage: .flux <prompt>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return
        await self.generate_image(message, args, "flux-pro")

    @loader.command(ru_doc="🚀 Сгенерировать фото, модель sd3. .sd3 <prompt>")
    async def sd3(self, message):
        """🚀 Generate image using sd3 model. Usage: .sd3 <prompt>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return
        await self.generate_image(message, args, "sdxl")

    @loader.command(ru_doc="🖼️ Сгенерировать изображение, модель pixart-alpha. .pixart <prompt>")
    async def pixart(self, message):
        """🖼️ Generate image using pixart-alpha model. Usage: .pixart <prompt>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return
        await self.generate_image(message, args, "pixart-alpha")

    @loader.command(ru_doc="🌐 Имеет поиск в интернете, использовать .gpt <запрос>")
    async def gpt(self, message):
        """🌐 Has internet search, usage: .gpt <query>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return

        await utils.answer(message, self.strings['generating'])

        try:
            response = await self.generate_text_with_gpt(args, "gpt-3-web")
            if response == "OLD_VERSION":
                await utils.answer(message, self.strings['old_version'])
            elif response == "IP_BLOCKED":
                await utils.answer(message, self.strings['ip_blocked'])
            elif response:
                lang = self.get_lang()
                query = "Query" if lang == "en" else "Запрос"
                await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>{query}:</b> <code>{args}</code>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{response}</b>')
            else:
                await utils.answer(message, self.strings['error'].format("Failed to get response from GPT."))
        except Exception as e:
            await utils.answer(message, self.strings['error'].format(str(e)))

    @loader.command(ru_doc="⚙️ Модель GPT-4, использовать .gpt4 <запрос>")
    async def gpt4(self, message):
        """⚙️ GPT-4 model, usage: .gpt4 <query>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return

        await utils.answer(message, self.strings['generating'])

        try:
            response = await self.generate_text_with_gpt(args, "gpt-4")
            if response == "OLD_VERSION":
                await utils.answer(message, self.strings['old_version'])
            elif response == "IP_BLOCKED":
                await utils.answer(message, self.strings['ip_blocked'])
            elif response:
                lang = self.get_lang()
                query = "Query" if lang == "en" else "Запрос"
                await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>{query}:</b> <code>{args}</code>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{response}</b>')
            else:
                await utils.answer(message, self.strings['error'].format("Failed to get response from GPT-4."))
        except Exception as e:
            await utils.answer(message, self.strings['error'].format(str(e)))

    @loader.command(ru_doc="🤖 Очень умная модель GPT-4o, использовать .gpt4o <запрос>")
    async def gpt4o(self, message):
        """🤖 Very smart GPT-4o model, usage: .gpt4o <query>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return

        await utils.answer(message, self.strings['generating'])

        try:
            response = await self.generate_text_with_gpt(args, "gpt-4o")
            if response == "OLD_VERSION":
                await utils.answer(message, self.strings['old_version'])
            elif response == "IP_BLOCKED":
                await utils.answer(message, self.strings['ip_blocked'])
            elif response:
                lang = self.get_lang()
                query = "Query" if lang == "en" else "Запрос"
                await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>{query}:</b> <code>{args}</code>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{response}</b>')
            else:
                await utils.answer(message, self.strings['error'].format("Failed to get response from GPT-4o."))
        except Exception as e:
            await utils.answer(message, self.strings['error'].format(str(e)))

    @loader.command(ru_doc="🔥 Умная модель GPT-4o-mini, использовать .gpt4om <запрос>")
    async def gpt4om(self, message):
        """🔥 Smart GPT-4o-mini model, usage: .gpt4om <query>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return

        await utils.answer(message, self.strings['generating'])

        try:
            response = await self.generate_text_with_gpt(args, "gpt-4o-mini")
            if response == "OLD_VERSION":
                await utils.answer(message, self.strings['old_version'])
            elif response == "IP_BLOCKED":
                await utils.answer(message, self.strings['ip_blocked'])
            elif response:
                lang = self.get_lang()
                query = "Query" if lang == "en" else "Запрос"
                await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>{query}:</b> <code>{args}</code>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{response}</b>')
            else:
                await utils.answer(message, self.strings['error'].format("Failed to get response from GPT-4o-mini."))
        except Exception as e:
            await utils.answer(message, self.strings['error'].format(str(e)))

    @loader.command(ru_doc="⚡️ Быстрая и умная модель GPT-4-Turbo, использовать .gpt4t <запрос>")
    async def gpt4t(self, message):
        """⚡️ Fast and smart GPT-4-Turbo model, usage: .gpt4t <query>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return

        await utils.answer(message, self.strings['generating'])

        try:
            response = await self.generate_text_with_gpt(args, "gpt-4-turbo")
            if response == "OLD_VERSION":
                await utils.answer(message, self.strings['old_version'])
            elif response == "IP_BLOCKED":
                await utils.answer(message, self.strings['ip_blocked'])
            elif response:
                lang = self.get_lang()
                query = "Query" if lang == "en" else "Запрос"
                await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>{query}:</b> <code>{args}</code>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{response}</b>')
            else:
                await utils.answer(message, self.strings['error'].format("Failed to get response from GPT-4-Turbo."))
        except Exception as e:
            await utils.answer(message, self.strings['error'].format(str(e)))

    @loader.command(ru_doc="🔎 Проверить обновления модуля")
    async def kupdate(self, message):
        """🔎 Check module updates"""
        module_name = "KsenonGPT"
        module = self.lookup(module_name)
        sys_module = inspect.getmodule(module)
        local_version = sys_module.version
        local_version_str = ".".join(map(str, local_version))

        headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://api.github.com/repos/TheKsenon/MyHikkaModules/contents/ksenongpt.py") as response:
                if response.status == 200:
                    data = await response.json()
                    remote_content = await (await session.get(data['download_url'])).text()
                    remote_lines = remote_content.splitlines()

                    try:
                        version_line = next(line for line in remote_lines if line.strip().startswith("version ="))
                        new_version = tuple(map(int, version_line.split("=", 1)[1].strip().strip("()").replace(",", "").split()))
                        new_version_str = ".".join(map(str, new_version))

                        changelog = next((line.split(":", 1)[1].strip() for line in remote_lines if line.startswith("# changelog:")), "No information")

                        if new_version > local_version:
                            await utils.answer(message, self.strings['update_available'].format(
                                new_version_str,
                                local_version_str,
                                changelog,
                                data['download_url']
                            ))
                        else:
                            await utils.answer(message, self.strings['latest_version'])
                    except StopIteration:
                        await utils.answer(message, self.strings['error'].format("Could not find version info in remote file."))
                    except Exception as e:
                        await utils.answer(message, self.strings['error'].format(f"Error processing version: {str(e)}"))
                else:
                    await utils.answer(message, self.strings['error'].format(f"Failed to check updates. Try again later. ({response.status})"))

    @loader.command(ru_doc="🔎 Искать в Google. Используй: .google <запрос>")
    async def google(self, message):
        """🔎 Search in Google. Usage: .google <query>"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit(self.strings['no_args'])
            return

        await message.edit(self.strings['searching'])

        query = args
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
                await message.edit(self.strings['no_results'])
                return

            output = "┏ <emoji document_id=5188311512791393083>🔎</emoji> <b>Google search results:</b>\n┃\n"

            for i, result in enumerate(search_results[:3], 1):
                title_elem = result.find("h3")
                description_elem = result.find("div", class_="VwiC3b")
                link_elem = result.find("a")

                title = title_elem.text if title_elem else "No title"
                description = description_elem.text.strip() if description_elem else "No description."
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "Link not found"

                output += f"┣ {i}️⃣ <b>{title}</b>\n"
                output += f"┣ 📑 <i>Description: {description}</i>\n"
                output += f"┣ 🌐 URL: <a href='{link}'>Link</a>\n┃\n"

            output += "┗ <emoji document_id=5427009714745517609>✅</emoji> KsenonGPT"
            await message.edit(output)

        except requests.RequestException as e:
            await message.edit(self.strings['error'].format(f"Request error: {e}"))
        except Exception as e:
            await message.edit(self.strings['error'].format(f"Unexpected error: {e}"))

    @loader.command(ru_doc="💬 Phi 3.5-Mini, использовать: .phi <запрос>")
    async def phi(self, message):
        """💬 Phi 3.5-Mini, usage: .phi <query>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings['no_args'])
            return

        await utils.answer(message, self.strings['generating'])

        try:
            response = await self.generate_phi_text(args)
            if response == "OLD_VERSION":
                await utils.answer(message, self.strings['old_version'])
            elif response == "IP_BLOCKED":
                await utils.answer(message, self.strings['ip_blocked'])
            elif response:
                lang = self.get_lang()
                query = "Query" if lang == "en" else "Запрос"
                await utils.answer(message, f'<emoji document_id=5443038326535759644>💬</emoji> <b>{query}:</b> <code>{args}</code>\n\n<emoji document_id=5372981976804366741>🤖</emoji> <b>{response}</b>')
            else:
                await utils.answer(message, self.strings['error'].format("Failed to get response from Phi."))
        except Exception as e:
            await utils.answer(message, self.strings['error'].format(str(e)))

    @loader.command(ru_doc="📰 Получить новости модулей")
    async def news(self, message):
        """📰 Get module news"""
        url = "https://github.com/TheKsenon/MyHikkaModules/raw/refs/heads/main/news.txt"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    news_text = await response.text()
                    await utils.answer(message, f"<emoji document_id=5433982607035474385>📰</emoji> <b>Module news:</b>\n\n<i><b>{news_text}</i></b>")
                else:
                    await utils.answer(message, self.strings['error'].format(f"Failed to get news. Try again later. ({response.status})"))
