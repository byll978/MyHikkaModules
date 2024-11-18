# ------------------------------------------------------------
# Module: CopyUser
# Description: One command, and you are already another.
# Author: @kmodules
# ------------------------------------------------------------
# Licensed under the GNU AGPLv3
# https:/www.gnu.org/licenses/agpl-3.0.html
# ------------------------------------------------------------
# Author: @MeKsenon
# Commands:
# scope: hikka_only
# meta developer: @kmodules
# ------------------------------------------------------------

from .. import loader, utils
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest # <-- ДЕЛЕТЕ ФОТО.
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError, ImageProcessFailedError
import io

@loader.tds
class CopyUserModule(loader.Module):
    """Module that copying another user."""

    strings = {"name": "CopyUser"}

    async def client_ready(self, client, db):
        self.client = client
        await self.client(JoinChannelRequest("kmodules"))

    @loader.command()
    async def copyuser(self, message):
        """Copy user.
         Use: .copy <username>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5832251986635920010>➡️</emoji><b>Provide username after command!</b>")
            return

        try:
            user = await message.client.get_entity(args)
            full_user = await message.client(GetFullUserRequest(user.id))
            
            if full_user.full_user.profile_photo:
                try:
                    avatar = await message.client.download_profile_photo(user, bytes)
                    if avatar:
                        photos = await message.client.get_profile_photos('me')
                        await message.client(DeletePhotosRequest(photos))
                        
                        await message.client(UploadProfilePhotoRequest(
                            file=await message.client.upload_file(io.BytesIO(avatar))
                        ))
                        await utils.answer(message, "<emoji document_id=5879770735999717115>👤</emoji><b>Avatar has been changed.</b>")
                    else:
                        await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji> <b>Error while changing avatar.</b>")
                except ImageProcessFailedError:
                    await utils.answer(message, "<emoji document_id=5210952531676504517>❌</emoji> <b>Error while processing the avatar.</b>")
            else:
                await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>The user does not have an avatar!</b>")
            
            await message.client(UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=full_user.full_user.about or ""
            ))
            
            await utils.answer(message, "<emoji document_id=5397916757333654639>➕</emoji> <b>User fully copied!</b>")
        except UsernameNotOccupiedError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>There is no user with this username!</b>")
        except UsernameInvalidError:
            await utils.answer(message, "<emoji document_id=5240241223632954241>🚫</emoji> <b>Invalid username format.</b>")
        except Exception as e:
            await utils.answer(message, f"😵 Ошибка: {str(e)}")
