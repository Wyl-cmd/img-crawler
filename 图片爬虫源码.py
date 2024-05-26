import os
import time
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'}


def check_page_existence(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查响应状态码
        if 'Page Not Found' in response.text:
            return False
        return True
    except requests.exceptions.RequestException as e:
        print('网页请求失败:', e)
        return False


def download_image(img_url, dir_path):
    time.sleep(1)
    try:
        img_response = requests.get(img_url, headers=headers, timeout=10)
        img_response.raise_for_status()  # 检查图片响应状态码
        if img_response.status_code == 200:
            file_name = re.sub('[/:*?"<>|]', '-', os.path.basename(urlparse(img_url).path))  # 处理非法字符
            with open(os.path.join(dir_path, file_name), 'wb') as f:
                f.write(img_response.content)
            print(f'{file_name} 下载完成')
        else:
            print(f'下载 {img_url} 失败: 响应状态码错误')
    except requests.exceptions.RequestException as e:
        print(f'下载 {img_url} 失败:', e)


def download_images_from_url(url, save_folder):
    if not check_page_existence(url):
        return

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查响应状态码

        dir_name = 'default_directory_name'
        soup = BeautifulSoup(response.content, 'html.parser')
        title_element = soup.find('h1')
        if title_element:
            dir_name = re.sub(r'[\\/*?:"<>|]+', '-', title_element.get_text().strip())  # 处理非法字符

        dir_path = os.path.join(save_folder, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        img_tags = soup.find_all('img', src=True)
        a_tags = soup.find_all('a', href=True)

        img_urls = [urljoin(url, tag['src']) for tag in img_tags if tag['src'].endswith(('.jpg', '.png'))]
        img_urls += [urljoin(url, tag['href']) for tag in a_tags if tag['href'].endswith(('.jpg', '.png'))]

        for img_url in img_urls:
            download_image(img_url, dir_path)

        print('图片爬取完成')

    except requests.exceptions.RequestException as e:
        print('网页请求失败:', e)


# 示例用法
input_url = input("请输入要爬取的网页URL：")
input_save_folder = input("请输入要保存图片的文件夹路径：")
download_images_from_url(input_url, input_save_folder)
