import os
import argparse
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv


def is_shorten_link(token, url):
    url_parts = urlparse(url)
    if url_parts.netloc != 'vk.cc' or len(url_parts.path) <= 1:
        return False

    response = requests.get(
        "https://api.vk.com/method/utils.getLinkStats",
        params={
            "access_token": token,
            "key": url_parts.path[1:],
            "v": "5.131"
        },
        timeout=3
    )
    response.raise_for_status()
    api_response = response.json()
    return 'error' not in api_response


def count_clicks(token, short_url):
    url_parts = urlparse(short_url)
    response = requests.get(
        "https://api.vk.com/method/utils.getLinkStats",
        params={
            "access_token": token,
            "key": url_parts.path[1:],
            "v": "5.131"
        },
        timeout=5
    )
    response.raise_for_status()
    stats_data = response.json()
    return sum(day['views'] for day in stats_data['response']['stats'])


def shorten_link(token, original_url):
    url_parts = urlparse(original_url)
    if not url_parts.scheme:
        original_url = f'https://{original_url}'

    response = requests.get(
        "https://api.vk.com/method/utils.getShortLink",
        params={
            "access_token": token,
            "url": original_url,
            "v": "5.131"
        },
        timeout=5
    )
    response.raise_for_status()
    link_info = response.json()
    return link_info['response']['short_url']


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description='VK URL Shortener and Click Counter')
    parser.add_argument('url', help='URL to process (shorten or count clicks)')
    args = parser.parse_args()

    try:
        token = os.environ['VK_API_TOKEN']
        url = args.url.strip()

        if is_shorten_link(token, url):
            clicks_count = count_clicks(token, url)
            print(f"Кликов: {clicks_count}")
        else:
            short_url = shorten_link(token, url)
            print(f"Сокращенная ссылка: {short_url}")

    except KeyError:
        print("Ошибка: Укажите VK_API_TOKEN в .env")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обращении к API VK: {str(e)}")
    except ValueError as e:
        print(f"Ошибка обработки данных: {str(e)}")
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")


if __name__ == "__main__":
    main()