import json
import urllib.request
import random
import shutil
import requests 
import os
import ctypes



sub_reddits = ['wallpaper', 'wallpapers', 'wallpaperdump', 'wallpaperengine', 'ImaginaryLandscapes', 
            'EarthPorn', 'food', 'foodphotography', 'LandscapePhotography', 'Minecraft', 'blender', 'skyporn']

def check_ext(img_url):
    for ext in img_exts:
        if img_url.endswith(ext):
            return True
    return False

def download_file(file_url, path):
    r = requests.get(file_url, allow_redirects=True)
    open(path, 'wb').write(r.content)

def get_ext(url):
    return url.split('.')[-1]

def change(offline_pic=None):
    try:
        if offline_pic:
            Fpath = os.path.realpath(os.getcwd())
            pic_path = os.path.join(os.sep, Fpath, 'pics', '{}'.format(offline_pic))
            ctypes.windll.user32.SystemParametersInfoW(20, 0, pic_path, 0)
        else:
            img_urls = []

            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'TE': 'Trailers'
            }
            random.shuffle(sub_reddits)
            for sub_reddit in sub_reddits:
                print('passing over', sub_reddit)
                req = requests.get('https://www.reddit.com/r/{}/.json'.format(sub_reddit), headers=headers)
                jsondata = req.json()
                # print(jsondata)
                posts = jsondata['data']['children']
                current_urls = [post['data']['url'] for post in posts if (post['data']['url']).split('.')[-1] in 
                ['jpg', 'jpeg', 'png'] and 'imgur' not in post['data']['url']]
                img_urls += current_urls
            print('found', img_urls)
            chosen_img = random.choice(img_urls)
            print('choose', chosen_img)
            download_file(chosen_img, 'pics/{}.{}'.format(chosen_img[::-8], get_ext(chosen_img)))
            Fpath = os.path.realpath(os.getcwd())
            pic_path = os.path.join(os.sep, Fpath, 'pics', '{}.{}'.format(chosen_img[::-8], get_ext(chosen_img)))
            ctypes.windll.user32.SystemParametersInfoW(20, 0, pic_path , 0)
    except Exception as e:
        print('error', e)
if __name__ == '__main__':
    change()
