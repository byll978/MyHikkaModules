from .. import loader, utils
import random
import asyncio
import os
import string
import subprocess

# meta developer: @kmodules
__version__ = (1, 0, 0)

@loader.tds
class RussianRouletteModule(loader.Module):
    """Русская рулетка. Немного безопаснее."""

    strings = {
        "name": "RussianRoulette", 
        "loaded": "🔫 <b>You loaded the gun.\n\n🔗 Bullet: {}/6</b>\n\n👁️‍🗨️ <b>Shoot?</b>",
        "lucky": "🙂 <b>You got lucky!\n\n🔗 The dangerous bullet was: {}\n👁️‍🗨️ Bullet: {}/6</b>",
        "unlucky": "🫨 <b>BANG! The bullet hit.\n\n😵‍💫 Punishment: {}</b>",
        "module_deleted": "🗑 Deleted module: {}",
    }

    strings_ru = {
        "name": "RussianRoulette",
        "loaded": "🔫 <b>Вы зарядили пистолет.\n\n🔗 Пуля: {}/6</b>\n\n👁️‍🗨️ <b>Стрелять?</b>",
        "lucky": "🙂 <b>Вам повезло!\n\n🔗 Опасной пулей была: {}\n👁️‍🗨️ Пуля: {}/6</b>",
        "unlucky": "🫨 <b>БАМ! Пуля попала.\n\n😵‍💫 Наказание: {}</b>",
        "module_deleted": "🗑 Удален модуль: {}",
    }

    async def _get_modules_path(self):
        try:
            if os.path.exists(os.path.expanduser("~/Hikka/loaded_modules")):
                result = subprocess.run("cd && cd Hikka && cd loaded_modules && ls", 
                                     shell=True, capture_output=True, text=True)
                return os.path.expanduser("~/Hikka/loaded_modules"), result.stdout.split()
            elif os.path.exists(os.path.expanduser("~/Heroku/loaded_modules")):
                result = subprocess.run("cd && cd Heroku && cd loaded_modules && ls", 
                                     shell=True, capture_output=True, text=True)
                return os.path.expanduser("~/Heroku/loaded_modules"), result.stdout.split()
        except:
            return None, []
        return None, []

    async def _delete_random_module(self):
        path, files = await self._get_modules_path()
        if path and files:
            random_file = random.choice(files)
            try:
                os.remove(os.path.join(path, random_file))
                return random_file
            except:
                pass
        return None

    async def _generate_random_prefix(self):
        symbols = string.ascii_letters + string.punctuation
        return random.choice(symbols)

    async def roulettecmd(self, message):
        """Начать игру в русскую рулетку"""
        self.bullet = random.randint(1, 6)
        current = random.randint(1, 6)

        buttons = [
            [
                {
                    "text": "🔫 Стрелять",
                    "callback": self.shoot_callback,
                    "args": (current,),
                },
                {
                    "text": "🔗 Реролл",
                    "callback": self.reroll_callback,
                    "args": (current,),
                },
            ]
        ]

        await self.inline.form(
            text=self.strings["loaded"].format(current),
            message=message,
            reply_markup=buttons,
        )

    async def shoot_callback(self, call, current):
        if current == self.bullet:
            punishments = [
                "Оставление юзербота", 
                "Удаление рандомного модуля", 
                "Перезапуск юзербота",
                "Рандомный префикс",
                "Удаление всех модулей"
            ]
            punishment = random.choice(punishments)
            
            await call.edit(
                self.strings["unlucky"].format(punishment)
            )

            if punishment == "Оставление юзербота":
                await asyncio.sleep(1)
                suspend_time = random.randint(30, 60)
                await self.invoke("suspend", f"{suspend_time}", message=call.form["message"])
            elif punishment == "Удаление рандомного модуля":
                deleted_module = await self._delete_random_module()
                if deleted_module:
                    await call.edit(
                        self.strings["unlucky"].format(punishment) + "\n\n" + 
                        self.strings["module_deleted"].format(deleted_module)
                    )
            elif punishment == "Перезапуск юзербота":
                await asyncio.sleep(1)
                await self.invoke("restart", "-f", message=call.form["message"])
            elif punishment == "Рандомный префикс":
                new_prefix = await self._generate_random_prefix()
                await self.invoke("setprefix", new_prefix, message=call.form["message"])
            else:
                path, _ = await self._get_modules_path()
                if path:
                    try:
                        for file in os.listdir(path):
                            os.remove(os.path.join(path, file))
                    except:
                        pass
                await asyncio.sleep(1)
                await self.invoke("restart", "-f", message=call.form["message"])
        else:
            new_current = random.randint(1, 6)
            new_bullet = random.randint(1, 6)
            self.bullet = new_bullet
            
            buttons = [
                [
                    {
                        "text": "🔫 Стрелять",
                        "callback": self.shoot_callback,
                        "args": (new_current,),
                    },
                    {
                        "text": "🔗 Реролл",
                        "callback": self.reroll_callback,
                        "args": (new_current,),
                    },
                ]
            ]
            await call.edit(
                self.strings["lucky"].format(new_bullet, new_current),
                reply_markup=buttons,
            )

    async def reroll_callback(self, call, current):
        self.bullet = random.randint(1, 6)
        new_current = random.randint(1, 6)
        
        buttons = [
            [
                {
                    "text": "🔫 Стрелять",
                    "callback": self.shoot_callback,
                    "args": (new_current,),
                },
                {
                    "text": "🔗 Реролл",
                    "callback": self.reroll_callback,
                    "args": (new_current,),
                },
            ]
        ]

        await call.edit(
            self.strings["loaded"].format(new_current),
            reply_markup=buttons,
        )
