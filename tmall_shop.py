# -*- coding: utf-8 -*-
import time
from shop import Shop
from xml_handler import writer


class TmallShop(Shop):

    def __init__(self, query, rank, postage, url):
        super(TmallShop, self).__init__(query, rank, postage, url)

    def craw(self, driver):
        func_list = [
            self.get_goods_name,
            self.get_shop_name,
            self.get_shop_qualification,
            self.get_normal_price_range,
            self.get_prompt_price_range,
            self.get_sell_count,
            self.get_commitment,
            self.get_comment,
            self.get_collect_number
        ]
        for func in func_list:
            self.check_auth_code(driver, self.url)
            func(driver)

    def get_goods_name(self, driver):
        self.goods_name = driver.find_element_by_class_name("tb-detail-hd").find_element_by_tag_name("h1").text
        print("商品名字: %s" % self.goods_name)

    def get_shop_name(self, driver):
        self.shop_name = driver.find_element_by_class_name("slogo-shopname").find_element_by_tag_name("strong").text
        print("店铺名字：%s" % self.shop_name)

    def get_shop_qualification(self, driver):
        url = driver.find_element_by_class_name("shop-intro").find_element_by_class_name("main-info").find_element_by_tag_name("a").get_attribute("href")
        print(url)
        driver.get(url)
        try:
            self.shop_qualification = driver.find_element_by_class_name("tm-shop-age-content").text
        except Exception as e:
            self.shop_qualification = ""
        print("店铺资质：%s" % self.shop_qualification)
        self.get_shop_score(driver)
        time.sleep(3)
        driver.back()
        driver.refresh()

    def get_normal_price_range(self, driver):
        price = driver.find_element_by_class_name("tm-price-panel").find_element_by_class_name("tm-price")
        prices = self.get_all_float(price.text)
        if len(prices) > 1:
            self.normal_price_range["lower_price"] = float(prices[0])
            self.normal_price_range["higher_price"] = float(prices[1])
        else:
            self.normal_price_range["lower_price"] = float(prices[0])
            self.normal_price_range["higher_price"] = float(prices[0])

        print("销售价格: %s" % str(self.normal_price_range))

    def get_prompt_price_range(self, driver):
        price = driver.find_element_by_xpath("//dl[@class='tm-promo-panel tm-promo-cur']").find_element_by_class_name("tm-price")
        prices = self.get_all_float(price.text)
        if len(prices) > 1:
            self.prompt_price_range["lower_price"] = float(prices[0])
            self.prompt_price_range["higher_price"] = float(prices[1])
        else:
            self.prompt_price_range["lower_price"] = float(prices[0])
            self.prompt_price_range["higher_price"] = float(prices[0])

        print("促销价格：%s" % str(self.prompt_price_range))

    def get_sell_count(self, driver):
        self.sell_count = self.get_number(driver.find_element_by_xpath("//li[@class='tm-ind-item tm-ind-sellCount']").find_element_by_class_name("tm-count").text)
        print("销量：%d" % self.sell_count)

    def get_commitment(self, driver):
        commitments = driver.find_element_by_class_name("tb-serPromise").find_elements_by_tag_name("li")
        self.commitments = set([commitment.text for commitment in commitments])
        print("卖家承若: %s" % str(self.commitments))

    def get_comment(self, driver):
        # 点击评论
        driver.find_element_by_id("J_TabBar").find_elements_by_tag_name("li")[1].find_element_by_tag_name("a").click()
        time.sleep(1)
        self.review_count = self.get_number(driver.find_element_by_class_name("J_ReviewsCount").text)
        review_details = driver.find_element_by_class_name("rate-filter").find_elements_by_tag_name("label")[1:]
        self.review_with_append_count = self.get_number(review_details[0].text)
        self.review_with_picture_count = self.get_number(review_details[1].text)

        print("评论总数：%d" % self.review_count)
        print("追加评论数: %d" % self.review_with_append_count)
        print("带图片评论数：%d" % self.review_with_picture_count)

    def get_collect_number(self, driver):
        self.collect_number = self.get_number(driver.find_element_by_id("J_CollectCount").text)
        print("收藏数量：%d" % self.collect_number)

    def get_all_attributes(self, all_commitments):
        item = list()
        item.append(str(self.rank))
        item.append("天猫")
        item.append(str(self.goods_name))
        item.append(str(self.shop_name))
        item.append(str(self.url))
        item.append(str(self.shop_qualification))
        item.append(str(self.sell_count))
        item.append(str(self.normal_price_range["lower_price"]))
        item.append(str(self.normal_price_range["higher_price"]))
        item.append(str(self.prompt_price_range["lower_price"]))
        item.append(str(self.prompt_price_range["higher_price"]))
        item.append("")
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
        item.append("0")
        item.append("0")
        item.append("0")
        item.append(str(self.postage))
        for commitment in all_commitments:
            if commitment in self.commitments:
                item.append(commitment)
            else:
                item.append("")
        return item





