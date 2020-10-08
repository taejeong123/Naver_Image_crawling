import sys, time, requests, os, path, glob, base64
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tqdm import trange

def read_txt(txt_root):
    f = open(txt_root, mode='rt', encoding='utf-8-sig')
    lines = f.readlines()
    names_list = []
    for line in lines:
        names_list.append(line.replace('\n', ''))
    f.close()
    return names_list

def slide_down(driver, range_count):
    for z in range(range_count):
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        more_btn = driver.find_element_by_css_selector('a.btn_more._more')
        try:
            more_btn.click()
        except NoSuchElementException:
            pass
        time.sleep(1)

def download_image(dest, name, src, cnt):
    if 'data:image/' in src: return

    img_data = requests.get(src).content
    img_save_path = os.path.join(dest, name + '_' + str(cnt) + '.jpg')
    with open(img_save_path, 'wb') as handler:
        handler.write(img_data)

if __name__ == "__main__":
    save_root = sys.argv[1] # 이미지 저장할 폴더
    txt_root = sys.argv[2] # 텍스트 파일이 들어있는 폴더
    max_image = int(sys.argv[3]) # 한 단어 당 가져올 이미지 개수

    if max_image >= 1000:
        print('\n Error: 네이버 이미지는 최대 1000건까지 검색됨')
        quit()

    txt_list = [read_txt(os.path.join(txt_root, x)) for x in os.listdir(txt_root) if '.txt' in x]
    txt_filename_list = [os.path.splitext(os.path.basename(x))[0] for x in os.listdir(txt_root) if '.txt' in x]

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # Not showing Chrome
        options.add_argument('--disable-gpu') # GPU settings
        options.add_experimental_option('excludeSwitches', ['enable-logging']) # 'DevTools listening ~' 메세지 제거
        driver = webdriver.Chrome('chromedriver.exe', options=options)

        for x in range(len(txt_list)):
            dest = os.path.join(save_root, str(txt_filename_list[x]))
            os.makedirs(dest, exist_ok=True)

            for y in trange(len(txt_list[x]), desc='<' + txt_filename_list[x] + '> loop'):
                name = txt_list[x][y]
                url = r'https://search.naver.com/search.naver?where=image&sm=tab_jum&query=' + name
                driver.get(url)

                slide_down(driver, 10) # scroll & more button click

                img_list = driver.find_elements_by_css_selector('div.photo_grid._box div.img_area._item a img')

                now_image_cnt = 0
                for img in img_list:
                    if now_image_cnt >= max_image: break

                    img_dest = os.path.join(dest, str(y) + '_' + name)
                    os.makedirs(img_dest, exist_ok=True)
                    download_image(img_dest, name, img.get_attribute("src"), now_image_cnt) # image download
                    now_image_cnt += 1

    except Exception as e:
        print(e)
    finally:
        driver.quit()