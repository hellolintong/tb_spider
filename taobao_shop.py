# -*- coding: utf-8 -*-

import time
import re
import copy
from shop import Shop


class TbShop(Shop):

    def __init__(self, query, rank, postage, url):
        super(TbShop, self).__init__(query, rank, postage, url)
        self.review_with_good_count = 0
        self.review_with_normal_count = 0
        self.review_with_bad_count = 0
        self.shop_ranker = 0

    def craw(self, driver):
        print("商品链接：%s" % self.url)
        func_list = [self.get_goods_name,
                     self.get_shop_name,
                     self.get_shop_qualification,
                     self.get_shop_ranker,
                     self.get_normal_price_range,
                     self.get_prompt_price_range,
                     self.get_sell_count,
                     self.get_commitment,
                     self.get_comment,
                     self.get_collect_number]

        for func in func_list:
            self.check_auth_code(driver, self.url)
            func(driver)

    def get_goods_name(self, driver):
        self.goods_name = driver.find_element_by_class_name("tb-main-title").text
        print("商品名字：%s" % self.goods_name)

    def get_shop_name(self, driver):
        self.shop_name = driver.find_element_by_class_name("tb-shop-name").text
        print("店铺名字：%s" % self.shop_name)

    def get_shop_qualification(self, driver):
        shop_qualification_converter = {'https://gtms01.alicdn.com/tps/i1/TB1zIlNFVXXXXXtXpXXxwHxIVXX-198-60.png': '黄金卖家',
                                        'https://gtms01.alicdn.com/tps/i1/TB1.8JIFVXXXXbSXVXXFHLvIVXX-198-45.png': '心级卖家',
                                         'https://gtms01.alicdn.com/tps/i1/TB1f2dMFVXXXXcCXpXXFHLvIVXX-198-45.png': '钻石卖家'}
        shop_qualification = driver.find_element_by_xpath("//a[@class='J_ShopInfoHeader tb-shop-info-bg']").find_element_by_tag_name("img").get_attribute("src")
        self.shop_qualification = shop_qualification_converter[shop_qualification]
        print("店铺资质：%s" % self.shop_qualification)

    def get_shop_ranker(self, driver):
        driver.get(driver.find_element_by_xpath("//div[@class='tb-shop-rank tb-rank-cap']").find_element_by_tag_name("a").get_attribute("href"))
        try:
            driver.find_element_by_xpath("//a[@class='sufei-tb-dialog-close sufei-tb-overlay-close']").click()
        except Exception as e:
            pass
        text = driver.find_element_by_class_name("sep").find_elements_by_tag_name("li")[0].text
        self.shop_ranker = self.get_number(text)
        print("店铺信用：%s" % self.shop_ranker)
        self.get_shop_score(driver)
        time.sleep(3)
        driver.back()
        driver.refresh()

    def get_normal_price_range(self, driver):
        price = driver.find_element_by_class_name("tb-rmb-num")
        prices = self.get_all_float(price.text)
        self.normal_price_range = {}
        if len(prices) > 1:
            self.normal_price_range["lower_price"] = float(prices[0])
            self.normal_price_range["higher_price"] = float(prices[1])
        else:
            self.normal_price_range["lower_price"] = float(prices[0])
            self.normal_price_range["higher_price"] = float(prices[0])
        print("销售价格: %s" % str(self.normal_price_range))

    def get_prompt_price_range(self, driver):
        self.prompt_price_range = copy.deepcopy(self.normal_price_range)
        try:
            price = driver.find_element_by_class_name("J_PromoPriceNum")
            prices = self.get_all_float(price.text)
            if len(prices) > 1:
                self.prompt_price_range["lower_price"] = float(prices[0])
                self.prompt_price_range["higher_price"] = float(prices[1])
            else:
                self.prompt_price_range["lower_price"] = float(prices[0])
                self.prompt_price_range["higher_price"] = float(prices[0])
            print("促销价格：%s" % str(self.prompt_price_range))
        except Exception as e:
            return

    def get_sell_count(self, driver):
        self.sell_count = self.get_number(driver.find_element_by_id("J_SellCounter").text)
        print("销量：%d" % self.sell_count)

    def get_commitment(self, driver):
        commitments = driver.find_element_by_id("J_tbExtra").find_elements_by_tag_name("dl")[0].find_elements_by_tag_name("a")
        self.commitments = set([commitment.text for commitment in commitments])
        print("卖家承若: %s" % str(self.commitments))

    def get_comment(self, driver):

        def get_count(review_detail):
            return self.get_number(re.findall(r'\d+', review_detail.find_element_by_class_name("tb-tbcr-num").find_element_by_tag_name("span").text)[0])

        self.review_count = self.get_number(driver.find_element_by_class_name("J_ReviewsCount").text)
        driver.find_element_by_id("J_TabBar").find_elements_by_tag_name("li")[1].find_element_by_tag_name("a").click()
        time.sleep(1)
        review_details = driver.find_element_by_xpath("//ul[@class='J_KgRate_Filter filtering']").find_elements_by_tag_name("li")
        self.review_with_picture_count = self.get_number(review_details[1].find_element_by_class_name("tb-tbcr-num").find_element_by_tag_name("span").text[1:-1])

        if len(review_details) == 5:
            # 有些页面没有追加评论
            self.review_with_picture_count = get_count(review_details[1])
            self.review_with_good_count = get_count(review_details[2])
            self.review_with_normal_count = get_count(review_details[3])
            self.review_with_bad_count = get_count(review_details[4])
            self.review_with_append_count = 0
        else:
            self.review_with_picture_count = get_count(review_details[1])
            self.review_with_append_count = get_count(review_details[2])
            self.review_with_good_count = get_count(review_details[3])
            self.review_with_normal_count = get_count(review_details[4])
            self.review_with_bad_count = get_count(review_details[5])

        print("评论总数：%d" % self.review_count)
        print("追加评论数: %d" % self.review_with_append_count)
        print("带图片评论数：%d" % self.review_with_picture_count)
        print("带好评数：%d" % self.review_with_good_count)
        print("带中评数：%d" % self.review_with_normal_count)
        print("带差评数：%d" % self.review_with_bad_count)

    def get_collect_number(self, driver):
        self.collect_number = self.get_number(driver.find_element_by_class_name("J_FavCount").text)
        print("收藏数量：%d" % self.collect_number)

    def get_all_attributes(self, all_commitments):
        item = list()
        item.append(str(self.rank))
        item.append("淘宝")
        item.append(str(self.goods_name))
        item.append(str(self.shop_name))
        item.append(str(self.url))
        item.append(str(self.shop_qualification))
        item.append(str(self.sell_count))
        item.append(str(self.normal_price_range["lower_price"]))
        item.append(str(self.normal_price_range["higher_price"]))
        item.append(str(self.prompt_price_range["lower_price"]))
        item.append(str(self.prompt_price_range["higher_price"]))
        item.append(str(self.shop_ranker))
        item.append(str(self.collect_number))
        item.append(str(self.shop_score["goods_describe_facticity"]["score"]))
        item.append(str(self.shop_score["goods_describe_facticity"]["rank"]))
        item.append(str(self.shop_score["seller_service"]["score"]))
        item.append(str(self.shop_score["seller_service"]["rank"]))
        item.append(str(self.shop_score["logistics_quality"]["score"]))
        item.append(str(self.shop_score["logistics_quality"]["rank"]))
        item.append(str(self.review_count))
        item.append(str(self.review_with_append_count))
        item.append(str(self.review_with_picture_count))
        item.append(str(self.review_with_good_count))
        item.append(str(self.normal_price_range))
        item.append(str(self.review_with_bad_count))
        item.append(str(self.postage))
        for commitment in all_commitments:
            if commitment in self.commitments:
                item.append(commitment)
            else:
                item.append("")
        return item




