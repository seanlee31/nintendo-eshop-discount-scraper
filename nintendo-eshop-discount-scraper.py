from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time
import urllib.request
import os
import errno
import shutil

### Available Filters Options [Click] ###
# browser.find_element_by_xpath('//*/label[@for="check-sale"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-dlc"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-demo"]').click()

### Available Platform Options [Click] ###
# browser.find_element_by_xpath('//*/label[@for="check-system-switch"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-system-3ds"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-system-wiiu"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-system-wii"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-system-ds"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-system-ios"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-system-android"]').click()

### Available Availability Options [Click] ###
# browser.find_element_by_xpath('//*/label[@for="check-availability-new"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-availability-now"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-availability-prepurchase"]').click()
# browser.find_element_by_xpath('//*/label[@for="check-availability-soon"]').click()

#############################################################################################################################
def get_region_code(region):
    if region == "US":
        code = ""
    if region == "Canada":
        code = "/en_CA"

    return code

def get_currency_code(region):
    if region == "US":
        code = "USD"
    if region == "Canada":
        code = "CAD"

    return code

def get_discount_information(console='switch', region='Canada'):
    console_opt = console
    region_code = get_region_code(region)
    currency = get_currency_code(region)
    region = region.lower()
    
    url = \
        'https://www.nintendo.com{}/games/game-guide?pv=true\\#filter/-|-|-|-|-|-|-|-|-|-|-|-|-|-|featured|des|-|-'.format(region_code)

    chrome_options = Options()
    chrome_options.add_argument('--disable-extensions')

    # chrome_options.add_argument("--no-startup-window") ## not working for unknown reason

    chrome_driver_path = \
        'C:\\Users\\sean8\\Downloads\\chromedriver_win32\\chromedriver.exe'
    browser = webdriver.Chrome(chrome_driver_path,
                            chrome_options=chrome_options)
    browser.get(url)
    print("[Status] Virtual browser has been started.\n")

    ## Perform Filter Option [Click]

    browser.find_element_by_xpath('//*/label[@for="check-sale"]').click()

    ## Perform Platform Option [Click]
    browser.find_element_by_xpath('//*/label[@for="check-system-{}"]'.format(console_opt)
                                    ).click()


    timeout = 5
    time.sleep(timeout)  # # wait for the page to load

    count = 0
    threshold = 10
    while count < threshold:
        time.sleep(1.5)
        if browser.find_element_by_id("btn-load-more").text == 'Load more games':
            browser.find_element_by_id("btn-load-more").click()
            print("[Virtual Browser] Load More Games!\n")

        count += 1

    inner_html = browser.page_source

    p_game_name = \
        r'<li style="opacity: 1; transform: matrix\(1, 0, 0, 1, 0, 0\); transform-origin: 50% 50% 0px;">[\s\S]*?<h3 class="b3">(.*)<\/h3>'
    p_release_date = \
        r'<li style="opacity: 1; transform: matrix\(1, 0, 0, 1, 0, 0\); transform-origin: 50% 50% 0px;">[\s\S]*?<p class="b4 row-date"><strong>Release[s|d]<\/strong>(.*?)<\/p>'
    p_game_cover_url = \
        r'<div class="boxart-container">[\s\S]*?<img src="(.*?)"'
    p_console = \
        r'<li style="opacity: 1; transform: matrix\(1, 0, 0, 1, 0, 0\); transform-origin: 50% 50% 0px;">[\s\S]*?<p class="b4" data-system=".*?">(.*?)<\/p>'
    p_prices = \
        r'<li style="opacity: 1; transform: matrix\(1, 0, 0, 1, 0, 0\); transform-origin: 50% 50% 0px;">[\s\S]*?<p class="b3 row-price">([\s\S]*?)<\/p>'
    p_sale_price = r'<strong.*?>(.*)<\/strong>'
    p_orig_price = r'<s class="strike">(.*)<\/s>'

    game_names = re.findall(p_game_name, inner_html)
    release_dates = re.findall(p_release_date, inner_html)
    game_cover_urls = re.findall(p_game_cover_url, inner_html)
    consoles = re.findall(p_console, inner_html)
    prices = re.findall(p_prices, inner_html)

    sale_prices = list()
    orig_prices = list()


    for price in prices:
        sale_price = re.findall(p_sale_price, price)[0]

        if sale_price != 'N/A':
            orig_price = re.findall(p_orig_price, price)[0]

            sale_prices.append(sale_price)
            orig_prices.append(orig_price)
        else:
            orig_price = 'N/A'

            sale_prices.append(sale_price)
            orig_prices.append(orig_price)

    browser.quit()
    print("[Status] Virtual browser has been closed. Data has been loaded into memory!\n")
    print("[Status] Start downloading game covers and writing details ...\n")

    game_dict = dict()

    if len(game_names) == len(release_dates) == len(sale_prices) \
        == len(orig_prices) == len(game_cover_urls):
        for i in range(len(game_names)):
            game_dict[str(i)] = {
                'game_name': game_names[i],
                'release_date': release_dates[i],
                'sale_price': sale_prices[i],
                'orig_price': orig_prices[i],
                'game_cover_url': game_cover_urls[i],
                'console': consoles[i]
                }
            if game_dict[str(i)]['sale_price'] == 'N/A':
                game_dict[str(i)]['price_difference'] = 'N/A'
            else:
                price_difference = float(game_dict[str(i)]['orig_price'][1:]) - float(game_dict[str(i)]['sale_price'][1:])
                game_dict[str(i)]['price_difference'] = str(round(price_difference, 2))

    else:
        print('[Error] The lengths of all attributes did not match.\n')
        exit()

    on_sale_games_txt_path = \
        './nintendo-game-sales/{}/{}/{}-on-sale-games-list.txt'.format(console_opt, region, console_opt)
    dir_path = os.path.dirname(on_sale_games_txt_path)

    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            print("[Main] Added folder for storing game covers and details!\n")
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise
    else:
        shutil.rmtree(dir_path)
        print("[Main] Removed old/expired discounts!\n")
        try:
            os.makedirs(dir_path)
            print("[Main] Re-added folder for storing discounted game covers and details!\n")
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise

    with open(on_sale_games_txt_path, 'w') as output:
        for i in range(len(game_dict)):
            line = ':'.join([                
                game_dict[str(i)]['sale_price'],
                game_dict[str(i)]['orig_price'],
                game_dict[str(i)]['release_date'],
                game_dict[str(i)]['game_cover_url']
                ])
            
            ## Parse invalid path characters
            game_name = re.findall(r'([\w\s]*)',
                                game_dict[str(i)]['game_name'])

            game_name.append('.png')
            game_name.insert(0, str(i + 1) + '. ')
            trimmed_game_name = ''.join(game_name)

            game_cover_path = './nintendo-game-sales/{}/{}/'.format(console_opt, region) + trimmed_game_name
            urllib.request.urlretrieve(game_dict[str(i)]['game_cover_url'],
                                    game_cover_path)

            
            
            output.write(str(i+1) + '. (' + game_dict[str(i)]['console'] + ') ')
            output.write("(Save ${} {}) ".format(game_dict[str(i)]['price_difference'], currency))
            output.write("[{}] ".format(game_dict[str(i)]['game_name']))
            output.write(line)
            # output.write()
            # output.write()
            # output.write()
            output.write('\n\n')

    print("[Status] Finished!")

if __name__ == "__main__":
    console_options = ['switch', '3ds', 'wiiu', 'wii', 'ds', 'ios', 'android']

    print("[Main] Please input the console you wish to check the game discounts on: ({})\n".format(', '.join(console_options)))
    console = input(">> ")
    print()

    if len(console) == 0:
        print("[Main] Did not recieve any input, using default console option: switch\n")
        console = 'switch'
    else:
        if console not in console_options:
            print("[Main] Did not recieve a valid input, using default console option: switch\n")
            console = 'switch'
    
    region_options = ['Canada', 'US']
    print("[Main] Please input the region you wish to check the game discounts on: ({})\n".format(', '.join(region_options)))
    region = input(">> ")
    print()

    if len(region_options) == 0:
        print("[Main] Did not recieve any input, using default region option: Canada\n")
        region = 'Canada'
    else:
        if region not in region_options:
            print("[Main] Did not recieve a valid input, using default region option: Canada\n")
            region = 'Canada'

    print("[Main] Start getting Nintendo {} game discounts!\n".format(console))
    get_discount_information(console=console, region=region)