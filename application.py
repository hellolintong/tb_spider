# -*- coding: utf-8 -*-

import traceback
import datetime
import time
import requests
import json
import urllib
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from shop import Shop
from taobao_shop import TbShop
from old_taobao_shop import OldTbShop
from tmall_shop import TmallShop
from xml_handler import writer


def query_stuff_rank(stuff, pages):
    ranks_list = []
    query_data = {
        "event_submit_do_new_search_auction": "1",
        "_input_charset": "utf-8",
        "topSearch": "1",
        "atype": "b",
        "searchfrom": "1",
        "action": "home:redirect_app_action",
        "from": "1",
        "q": stuff,
        "sst": "1",
        "n": "20",
        "buying": "buyitnow",
        "m": "api4h5",
        "abtest": "10",
        "wlsort": "10",
        "page": "1"
    }
    for i in range(1, pages, 1):
        query_data["page"] = str(i)
        url = r"https://s.m.taobao.com/search?" + urllib.parse.urlencode(query_data)
        ranks = requests.get(url)
        if ranks.status_code == requests.codes.ok:
            taobao_url = "https://item.taobao.com/item.htm?spm=a230r.1.14.44.42ff6509EijNTq&id=%s&ns=1&abbucket=4#detail"
            tmall_url = "https://detail.tmall.com/item.htm?spm=a230r.1.14.6.42ff6509EijNTq&id=%s&cm_id=140105335569ed55e27b&abbucket=4"
            ranks_content = json.loads(ranks.text)
            print(ranks_content)
            for item in ranks_content["listItem"]:
                if "tmall" in item["url"]:
                    ranks_list.append({"url": tmall_url % item["item_id"],
                                       "postage": item["fastPostFee"]})
                elif "mclick" in item["url"]:
                    ranks_list.append({"url": item["url"],
                                      "postage": item["fastPostFee"]})
                else:
                    ranks_list.append({"url": taobao_url % item["item_id"],
                                      "postage": item["fastPostFee"]})
            for rank in ranks_list:
                print(rank)
            time.sleep(5)
    return ranks_list


def crawling_shop(driver, query, shop_url, rank, postage):
    driver.get(shop_url)
    driver.refresh()
    time.sleep(5)

    if "tmall" in shop_url:
        return crawling_tmall_shop(driver, query, rank, postage, shop_url)

    # mclick 对应的链接有不确定性，所以两种都试下
    elif "mclick" in shop_url:
        try:
            return crawling_tmall_shop(driver, query, rank, postage, shop_url)
        except Exception as e:
            return crawling_tb_shop(driver, query, rank, postage, shop_url)
    else:
        return crawling_tb_shop(driver, query, rank, postage, shop_url)


def crawling_tmall_shop(driver, query, rank, postage, url):
    tmall_shop = TmallShop(query=query, rank=rank, postage=postage, url=url)
    tmall_shop.craw(driver)
    return tmall_shop


def crawling_tb_shop(driver, query, rank, postage, url):
    tb_shop = TbShop(query=query, rank=rank, postage=postage, url=url)
    try:
        tb_shop.craw(driver)
    except Exception as e:
        print(e)
        time.sleep(3)
        driver.get(url)
        driver.refresh()
        # 可能用的是旧淘宝页面
        tb_shop = OldTbShop(query=query, rank=rank, postage=postage, url=url)
        tb_shop.craw(driver)
    return tb_shop


def write_shop(filename, shop_list, titles):
    all_commitment = set()
    for shop in shop_list:
        all_commitment |= shop.commitments

    all_commitment = list(all_commitment)
    titles.extend(all_commitment)
    items = [shop.get_all_attributes(all_commitment) for shop in shop_list]
    writer(filename, titles, items)


def login(driver):
    """
    """
    try:
        driver.get("https://login.tmall.com/?spm=875.7931836/B.a2226mz.1.66144265CV6xqC&redirectURL=https%3A%2F%2Fwww.tmall.com%2F")
        time.sleep(30)
        return True
    except Exception as e:
        return False


if __name__ == "__main__":
    shop_list = []
    query = input("输入需要检索的关键字:")

    ranks_list = query_stuff_rank(query, 2)

    #binary = FirefoxBinary("/Applications/Firefox.app/Contents/MacOS/firefox-bin")
    #driver = webdriver.Firefox(firefox_binary=binary)
    #driver = webdriver.PhantomJS("phantomjs")
    driver = webdriver.Chrome()
    driver.implicitly_wait(4)  # seconds
    driver.maximize_window()
    login(driver)
    # 在这里进行登陆操作
    time.sleep(5)

    ranks_list = ranks_list[:2]
    for idx, rank in enumerate(ranks_list):
        try:
            for i in range(3):
                try:
                    shop = crawling_shop(driver, query, rank["url"], idx, rank["postage"])
                    shop_list.append(shop)
                    driver.get("http://tmall.com")
                    driver.refresh()
                    time.sleep(10)
                    break
                except Exception as e:
                    tb = traceback.format_exc()
                    print(tb)
                    time.sleep(10)
                    print("爬取失败， 错误为:%s" % str(e))
                    driver.get("http://tmall.com")
                    driver.refresh()
                    pass
        except Exception as e:
            break
            """
            driver.close()
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get("https://www.tmall.com")
            """

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    write_shop("data/" + now + "_" + query + ".xls", shop_list, Shop.get_titles())

    #crawling_shop("https://item.taobao.com/item.htm?id=45034830880&ali_refid=a3_430125_1006:1110981262:N:%E6%B0%B4%E9%BE%99%E5%A4%B4+%E5%86%B7%E7%83%AD:5e4a37ed2a4940a4b1fd1d0eab2c3221&ali_trackid=1_5e4a37ed2a4940a4b1fd1d0eab2c3221")
    #crawling_shop("https://item.taobao.com/item.htm?spm=a230r.1.14.299.56086509tTgXBv&id=562485213887&ns=1&abbucket=4#detail")
    #crawling_shop("https://item.taobao.com/item.htm?spm=a230r.1.14.196.56086509tTgXBv&id=524926641449&ns=1&abbucket=4#detail")
    #crawling_shop("https://detail.tmall.com/item.htm?spm=a230r.1.14.6.42ff6509EijNTq&id=553639114029&cm_id=140105335569ed55e27b&abbucket=4")

