import requests
import pandas as pd
import string


def get_response(access_token, ver, domain, count, offset):
    response = requests.get('http://api.vk.com/method/wall.get',
                            params={
                                'access_token': access_token,
                                'v': ver,
                                'domain': domain,
                                'count': count,
                                'offset': offset
                            })
    return response.json()['response']['items']


def get_group_id_by_name(access_token, ver, group_name):
    response = requests.get('http://api.vk.com/method/groups.getById',
                            params={
                                'access_token': access_token,
                                'v': ver,
                                'group_id': group_name
                            })
    return response.json()['response'][0]['id']


if __name__ == '__main__':

    # create an app there https://vk.com/editapp?act=create and get Service token in the Settings tab
    token = '8830f81f8830f81f8830f81ff28844636f888308830f81fd7a7a4571166c6219f5f4bc1'
    ver_api = 5.124
    groupName = 'konturgusya'  # name from address bar (vk.com/<name>)
    groupId = None
    try:
        groupId = get_group_id_by_name(token, ver_api, groupName)
    except KeyError:
        exit('Bad token')
    count_of_posts = 100  # vk maximum is 100
    begin_from = 1  # post number where to begin from (offset)
    offset_cap = 400
    list_to_find = ['картинка', 'кто']
    df = pd.DataFrame()  # gonna save result here

    while begin_from < offset_cap:

        data = get_response(token, ver_api, groupName, count_of_posts, begin_from)

        try:
            for i in range(count_of_posts):
                text, post_id = data[i]['text'], data[i]['id']
                text_prepared = ''.join([j for j in text.lower() if j not in string.punctuation])
                try:
                    author_id = data[i]['signer_id']
                except KeyError:  # if no signer
                    author_id = None
                author_link = f'https://vk.com/id{author_id}\n' if author_id else None
                post_link = f'https://vk.com/{groupName}?w=wall-{groupId}_{post_id}'
                for word in list_to_find:
                    if word in text_prepared.split():
                        df = df.append(pd.DataFrame([{'text': text[:50], 'author': author_link, 'link': post_link}]),
                                       ignore_index=True)
        except IndexError:
            continue

        begin_from += count_of_posts

    # print(df)
    df.to_excel('output.xlsx')
