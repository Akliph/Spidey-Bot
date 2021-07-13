import requests
import pastelink_resolve
import binbucks_resolve


def resolve_link(link):
    redirect = requests.get(link).url

    if 'blogspot' in redirect:
        print("This is a blogspot redirect")
        resolved = pastelink_resolve.resolve_bitly_to_mega(link)
    elif 'binbucks' in redirect:
        print("This is a binbucks redirect")
        resolved = binbucks_resolve.resolve_entire_link(link)
    else:
        return False

    return resolved