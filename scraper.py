import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import io

def createChromeDrive():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def get_images_from_google(driver, delay, max_images):
    print("get_images_from_google")
    image_count  = 0;
    image_urls = set()

    thumbnails = driver.find_elements(By.CSS_SELECTOR, '.F0uyec')
        
    for img in thumbnails:
        if image_count > max_images:
            break
        try:
            img.click()
            time.sleep(delay)
        except:
            print("error occurred while clicking in the thumbnail")
            continue

        images = driver.find_elements(By.CSS_SELECTOR, '.p7sI2, .PUxBg')
        for container in images:
            image_count += 1
            img_tag = container.find_element(By.TAG_NAME, 'img')
            src = img_tag.get_attribute('src')
            
            if src and src.startswith('http') and src not in image_urls and 'encrypted' not in src:
                image_urls.add(src)
                image_count += 1
                break         

    return image_urls

def download_image(download_path, url, file_name):
    print(f"download_image: download_path:{download_path},url:{url},filename:{file_name}")
    try:
        image_content = requests.get(url,verify=False).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)

        if image.format not in ["JPEG", "PNG"]:
            print(f"Skipping image with unsupported format: {url}")
            return

        file_path = os.path.join(download_path, file_name)

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")

        print("Success")
    except Exception as e:
        print('FAILED -', e)



if __name__ == '__main__':
     # search_query = input("Enter your Google Images search query: ")
    search_query = 'portrait photo site:unsplash.com'
    search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"

    os.makedirs("rostos", exist_ok=True)

    driver = createChromeDrive()

    driver.get(search_url)

    urls = get_images_from_google(driver, 2, 2)
        
    for i, url in enumerate(urls):
         download_image("rostos", url, str(i) + ".jpg")

    driver.quit()
