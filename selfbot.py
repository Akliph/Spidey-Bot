import random

import requests
import os
import json


def retrieve_messages(channel_id):
    headers = {
        'authorization': 'mfa.jwmvF2zAUrhg4Cxd1Xx6_7spTR5k513pPLh4yYAh_hgkpO-YV5hw7rEpBXYNoYqzRJj3F4kUE7YY8qqGLX_S'
    }

    r = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)

    response = json.loads(r.text)

    try:
        if response['message'] == '401: Unauthorized':
            return False
    except:
        return response


def add_link_to_cache(unresolved, resolved, image=None, message=None):
    with open('./cache.json', 'r+') as f:
        data = json.load(f)

        data.append(
            {
                'unresolved': unresolved,
                'resolved': resolved,
                'image': image,
                'message': message
            }
        )

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
        f.close()


def pull_link_from_cache(unresolved, pull_image=False, pull_content=False):
    with open('./cache.json', 'r') as f:
        if os.stat('./cache.json').st_size == 0:
            return False

        data = json.load(f)

        for link in data:
            if link['unresolved'] == unresolved:
                if not pull_image:
                    return link['resolved']
                try:
                    return link['resolved'], link['image']
                finally:
                    return link['resolved']

        return False


def pull_all_data_from_cache():
    with open('./cache.json', 'r') as f:
        data = json.load(f)
        return data
        f.close()


if __name__ == '__main__':
    print(len(retrieve_messages(796166200555470878)))
    # start_time = time.time()
    # print(resolve_bitly_to_mega('https://bit.ly/2TRuQ3D'))
    # print(f'It took: {time.time() - start_time}')
    pass
