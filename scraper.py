import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import io
from multiprocessing import Process

def createChromeDrive():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def get_next_file_index(folder):
    existing_files = os.listdir(folder)
    indexes = []
    for name in existing_files:
        try:
            idx = int(os.path.splitext(name)[0])
            indexes.append(idx)
        except:
            continue
    return max(indexes, default=-1) + 1

def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url, verify=False).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)

        if image.format not in ["JPEG", "PNG"]:
            print(f"Skipping unsupported format: {url}")
            return False

        file_path = os.path.join(download_path, file_name)

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")

        print(f"Downloaded: {file_path}")
        return True
    except Exception as e:
        print(f"FAILED - {url} - {e}")
        return False

def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def get_images_from_google(driver, delay, max_images, folder):
    print("get_images_from_google")
    image_count = 0
    image_urls = set()
    index = get_next_file_index(folder)
    seen_thumbnails = set()
    
    while image_count < max_images:
        thumbnails = driver.find_elements(By.CSS_SELECTOR, '.F0uyec')
        
        for i, thumb in enumerate(thumbnails):
            if image_count >= max_images:
                break
            if i in seen_thumbnails:
                continue

            seen_thumbnails.add(i)

            try:
                thumb.click()
                time.sleep(delay)
            except Exception as e:
                print(f"Error clicking thumbnail {i}: {e}")
                continue

            images = driver.find_elements(By.CSS_SELECTOR, '.p7sI2, .PUxBg')
            for container in images:
                try:
                    img_tag = container.find_element(By.TAG_NAME, 'img')
                    src = img_tag.get_attribute('src')
                    if src and src.startswith('http') and src not in image_urls and 'encrypted' not in src:
                        if download_image(folder, src, f"{index}.jpg"):
                            image_urls.add(src)
                            image_count += 1
                            index += 1
                            break
                except Exception as e:
                    continue

        scroll_to_bottom(driver)

    return image_urls

def runScraper(termo):
    search_query = termo
    search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"

    folder = termo
    os.makedirs(folder, exist_ok=True)

    driver = createChromeDrive()
    driver.get(search_url)

    get_images_from_google(driver, delay=1, max_images=150, folder=folder)

    driver.quit()


if __name__ == '__main__':
    termos_de_pesquisa = [
        '',
    ]

    processos = []

    for termo in termos_de_pesquisa:
        p = Process(target=runScraper, args=(termo,))
        processos.append(p)
        p.start()

    for p in processos:
        p.join()