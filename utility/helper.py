import random
import string
from bs4 import BeautifulSoup
from .constants import LOCKED_VIDEO_PIC
from django.conf import settings
import vimeo

def gen_random_upper_str(N=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

def gen_random_lower_str(N=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=N))

def gen_random_str(N=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=N))

def generate_locked_content(html_str):
    soup = BeautifulSoup(html_str, "html.parser")

    # finding which tag come first from below list of tags in text.
    target_name = None
    target_index = -1
    tag_name_list = ('img', 'iframe', 'video')
    for tag_name  in tag_name_list:
        temp_index = html_str.find(f'<{tag_name}')
        if temp_index != -1 and (target_index == -1 or temp_index < target_index):
            target_index = temp_index
            target_name = tag_name

    # eliminating all next siblings of target and its parent targets
    target = soup.find(target_name)
    while True:
        if target:
            eliminate_tags = target.find_next_siblings()
            for tag in eliminate_tags:
                tag.decompose()
            # assignin target's parent to it target element
            target = target.parent
        else:
            break

    video_tags = soup.find_all('iframe')
    for video_tag in video_tags:
        thumbnail = get_vimeo_thumbnail(video_tag.get('src'))
        # replacing video with thumbnail.
        video_tag.replace_with(BeautifulSoup(get_locked_poster(thumbnail)))
    
    locked_ribbon = """
        <div class="locked-ribbon">
          <p>This post is locked. Please subscribe to access it.</p>
          <p><a href="/courses">Subscribe now</a></p>
          <p>Subscribed already? <a href="/login">Login</a></p>
        </div>
    """
    return str(soup).strip() + locked_ribbon

def get_locked_poster(thumbnail = None):
    return f"""
        <div class="locked-poster">
          <img src="{thumbnail if thumbnail else f'{settings.MEDIA_URL}{LOCKED_VIDEO_PIC}'}" alt="" />
          <div class="locked-layer">
            <div></div>
            <div class="box">
              <span class="ico"><i class="fa-solid fa-lock"></i></span>
              <p>This video is only for subscribed user.</p>
              <a class="btn pri" href="/courses">Subscribe Now</a>
            </div>
          </div>
        </div>
    """

def get_vimeo_thumbnail(video_url: str):
    if video_url and '//player.vimeo.com/video/' in video_url:
        video_id = video_url.split('//player.vimeo.com/video/')[-1]
        client = vimeo.VimeoClient(
            token=settings.VIMEO_ACCESS_TOKEN,
            key=settings.VIMEO_CLIENT_ID,
            secret=settings.VIMEO_CLIENT_SECRET
        )
        uri = f"https://api.vimeo.com/videos/{video_id}/pictures"
        response = client.get(uri)
        if response.status_code == 200:
            response_json = response.json()
            try:
                all_sizes = response_json['data'][0]['sizes']
                req_size = {'width': None, 'height': None, 'link': None}
                for size in all_sizes:
                    req_size['width'] = size['width']
                    req_size['height'] = size['height']
                    req_size['link'] = size['link']
                    if size['width'] >= 960 and req_size['height']:
                        break
                return req_size['link'] if req_size['link'] else None
            except: return None
    return None