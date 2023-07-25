import aiohttp

import config


class Trello:

    def __init__(self):
        pass

    """ Получение карточек по листу """
    async def get_board_tasks(self, api_key, token, list_id):
        url = f"https://api.trello.com/1/lists/{list_id}/cards"
        query_string = {"key": api_key, "token": token,}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query_string) as response:

                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception("Failed to get Trello tasks.")

    """ Получение всех досок привязанных к аккаунту пользователя"""
    async def get_all_boards(self, api_key, token):
        url = 'https://api.trello.com/1/members/me/boards?fields=id,name,url'
        query_string = {
            "key": api_key,
            "token": token,
            'dateTime': 'Europe/Moscow'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query_string) as response:

                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception("Failed to get Trello tasks.")

    """ Получение столбцов по ID досок"""
    async def get_all_lists(self, api_key, token, desk_id):
        url = f'https://api.trello.com/1/boards/{desk_id}/lists'
        query_string = {
            "key": api_key,
            "token": token,
            "dateTime": "Europe/Moscow"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query_string) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception("Failed to get Trello tasks.")

    """Получение меток направлений по ID карточки"""
    async def get_labels(self, api_key, token, card_id):

        url = f"https://api.trello.com/1/cards/{card_id}/labels"
        query_string = {
            "key": api_key,
            "token": token,
            "dateTime": "Europe/Moscow"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query_string) as response:

                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception("Failed to get Trello tasks.")
