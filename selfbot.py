import random

import requests
import os
import json


def retrieve_messages(channel_id):
    headers = {
        'authorization': 'ODU4MDM5MzA1MDI5Mjg3OTY2.YNYW_Q.D5Hh5Q8cVWLis5F9r8L52yVQQRs'
    }

    r = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)

    response = json.loads(r.text)

    return response


def add_link_to_cache(unresolved, resolved, image=None):
    with open('./cache.json', 'r+') as f:
        data = json.load(f)

        data.append(
            {
                'unresolved': unresolved,
                'resolved': resolved,
                'image': image
            }
        )

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
        f.close()


def pull_link_from_cache(unresolved, pull_image=False):
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
