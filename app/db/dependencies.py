import aiohttp
import os

VK_SERVICE = os.getenv("VK_SERVICE")


async def vk_get_names(vk_user_id: int):
    url = f"https://api.vk.com/method/users.get?user_ids={vk_user_id}&fields=first_name,last_name&access_token={VK_SERVICE}&v=5.131&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            user_info = data["response"][0]
            return user_info["first_name"], user_info["last_name"]
