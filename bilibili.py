"""
爬取bilibili
"""
import time
import random
from webbrowser import get
import requests
import re
import json

from scipy import rand

custom_headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    'Connection': 'close'
}


def get_dict(bvid: str) -> dict:
    """
    从单个网页中爬取需要的字典, 如果发生错误会直接扔出错误而不是返回None
    :param bvid: BV号
    :return: 需要的数据字典
    """
    # 请求原始html数据
    url = f"https://www.bilibili.com/video/{bvid}"
    response = requests.get(url=url, headers=custom_headers)
    if response.status_code != 200:
        ValueError(f"get html failed, status_code: {response.status_code}")

    # 使用正则表达式匹配出javaScript代码中的一个字典变量
    match = re.search(r"<script>window.__INITIAL_STATE__=(?P<dict>{.*?});", response.text, re.MULTILINE | re.DOTALL)
    if match is None:
        ValueError("dict not found")

    # 将匹配到的字符串转化为python字典
    video_dict = match.group('dict')
    dic = json.loads(video_dict)
    # 强行让你睡眠一秒, 防止进橘子
    time.sleep(random.random())
    return dic

def produce_json(dic: dict) -> dict:
    try:
        data = {
        'bvid': dic['bvid'],
        'title': dic['videoData']['title'],
        'state': dic['videoData']['stat'],
        'tags': [],
        }
        for tag in dic['tags']:
            data['tags'].append(tag['tag_name'])
    except KeyError as e:
        data = {
            'bvid': '',
            'title': '',
            'state': '',
            'tags': [],
        }

        # for item in dic['related']:
        #     data['related'].append({
        #         'bvid': item['bvid'],
        #         'title': item['title']
        #     })
            
        # bvList = []
        # for item in data['related']:
        #     bvList.append(item['bvid'])
    return data

def get_related(dic: dict) -> set:
    bvList = []
    try:
        for item in dic['related']:
            bvList.append(item['bvid'])
    except KeyError as e:
        pass
    return bvList

# 广度优先遍历进行爬取
def width(bvid: str):
    count = 0
    queue = set()
    passList = set()
    queue.add(bvid)
    passList.add(bvid)
    with open('result.txt', 'ab') as f:
        while queue and count < 300000:
            bvid = queue.pop()
            passList.add(bvid)
            dic = get_dict(bvid)
            f.write(json.dumps(produce_json(dic), ensure_ascii=False).encode('utf-8'))
            f.write(',\n'.encode('utf-8'))
            count = count + 1
            child = set(get_related(dic)).difference(passList)
            if child is not None:
                queue.update(child)

def main():
    while True:
        try:
            source = "BV1JB4y1s7Dk"
            width(source)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print('\n'+message)
            break
        finally:
            break

    


if __name__ == '__main__':
    main()
