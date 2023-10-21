import aiohttp
import time

class Kaiten:

    def __init__(self):
        pass

    # """ Получение карточек по листу """
    # async def get_board_tasks(self, api_key, domain, column_id):
    #     domain = domain[0]
    #     api_key = api_key[0]
    #     url = f"https://{domain}.kaiten.ru/api/latest/cards"
    #     headers  = {
    #         'Authorization': f'Bearer {api_key}',
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #     }
    #     params = {
    #         'column_id': f'{column_id}'
    #     }


    #     async with aiohttp.ClientSession() as session:
    #         content = []
    #         response = await session.get(url=url, headers=headers, params=params)
    #         time.sleep(0.25)

    #         if response.status == 200:
    #             content.append(await response.json(encoding='UTF-8'))
    #             return content
    #         else:
    #             raise Exception("Failed to get Trello tasks.")

    """ Получение всех пространств привязанных к аккаунту пользователя"""
    async def get_all_spaces(self, api_key, domain):
        domain = domain[0]
        api_key = api_key[0]
        url = f'https://{domain}.kaiten.ru/api/latest/spaces'
        
        headers  = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            content = []
            response = await session.get(url=url, headers=headers)
            time.sleep(0.25)
            if response.status == 200:
                content.append(await response.json(encoding='UTF-8'))
                return content
            else:
                raise Exception("Failed to get Trello tasks.")
            
    """ Получение всех досок привязанных к аккаунту пользователя"""
    async def get_all_boards(self, api_key, domain, space_id):
        domain = domain[0]
        api_key = api_key[0]
        url = f'https://{domain}.kaiten.ru/api/latest/spaces/{space_id}/boards'
        
        headers  = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            content = []
            response = await session.get(url=url, headers=headers)
            time.sleep(0.25)
            if response.status == 200:
                content.append(await response.json(encoding='UTF-8'))
                return content

            else:
                raise Exception("Failed to get Trello tasks.")
            
    ''' Получение доски по ID'''
    async def get_board(self, api_key, domain, board_id):
        domain = domain[0]
        api_key = api_key[0]
        url = f'https://{domain}.kaiten.ru/api/latest/boards/{board_id}'
        
        
        headers  = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            content = []
            response = await session.get(url=url, headers=headers)
            time.sleep(0.25)

            if response.status == 200:
                content.append(await response.json(encoding='UTF-8'))
                return content
            else:
                raise Exception("Failed to get Trello tasks.")


    # """ Получение столбцов по ID досок"""
    # async def get_all_lists(self, api_key, domain, board_id):
    #     domain = domain[0]
    #     api_key = api_key[0]
    #     url = f'https://{domain}.kaiten.ru/api/latest/boards/{board_id}/columns'
    #     headers  = {
    #         'Authorization': f'Bearer {api_key}',
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #     }

    #     async with aiohttp.ClientSession() as session:
    #         content = []
    #         response = await session.get(url=url, headers=headers)
    #         time.sleep(0.25)

    #         if response.status == 200:
    #             content.append(await response.json(encoding='UTF-8'))
    #             return content
    #         else:
    #             raise Exception("Failed to get Trello tasks.")

    # """Получение меток направлений по ID карточки"""
    # async def get_labels(self, api_key, domain, card_id):

    #     domain = domain[0]
    #     api_key = api_key[0]
    #     url = f"https://{domain}.kaiten.ru/api/latest/cards/{card_id}/tags"
    #     headers  = {
    #         'Authorization': f'Bearer {api_key}',
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #     }

    #     async with aiohttp.ClientSession() as session:
    #         content = []
    #         response = await session.get(url=url, headers=headers)
    #         time.sleep(0.25)

    #         if response.status == 200:
    #             content.append(await response.json(encoding='UTF-8'))
    #             return content
    #         else:
    #             raise Exception("Failed to get Trello tasks.")
