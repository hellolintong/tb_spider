# -*- coding: utf-8 -*-

from collections import defaultdict
import re
import time


class Shop:
    def __init__(self, query, rank, postage, url):
        self.query = query
        self.rank = rank
        self.postage = postage
        self.url = url
        self.goods_name = ""
        self.shop_name = ""
        self.shop_qualification = ""
        self.shop_score = defaultdict(dict)
        self.normal_price_range = {"lower_price": 0, "higher_price": 0}
        self.prompt_price_range = {"lower_price": 0, "higher_price": 0}
        self.sell_count = 0
        self.commitments = []
        self.review_count = 0
        self.review_with_append_count = 0
        self.review_with_picture_count = 0
        self.collect_number = 0

    @staticmethod
    def get_number(element):
        return int(re.findall(r'\d+', element)[0])

    @staticmethod
    def get_all_numbers(element):
        return [int(n) for n in re.findall(r'\d+', element)]

    @staticmethod
    def get_float(element):
        return float(re.findall(r'\d+\.?\d*', element)[0])

    @staticmethod
    def get_all_float(element):
        return [float(s) for s in re.findall(r'\d+\.?\d*', element)]

    def get_score_rank(self, element):
        m = element.find_element_by_tag_name("strong")
        class_name = m.get_attribute("class")
        if class_name == "percent normal":
            return 0
        elif class_name == "percent lower":
            return float(self.get_number(m.text)) * 0.01 * -1
        else:
            return float(self.get_number(m.text)) * 0.01

    def get_shop_score(self, driver):
        dsr_items = driver.find_elements_by_xpath("//li[@class='J_RateInfoTrigger dsr-item selected']")
        dsr_items.extend(driver.find_elements_by_xpath("//li[@class='J_RateInfoTrigger dsr-item']"))
        self.shop_score = defaultdict(dict)
        self.shop_score["goods_describe_facticity"]["score"] = self.get_float(dsr_items[0].find_element_by_class_name("count").text)
        self.shop_score["goods_describe_facticity"]["rank"] = self.get_score_rank(dsr_items[0])

        self.shop_score["seller_service"]["score"] = self.get_float(dsr_items[1].find_element_by_class_name("count").text)
        self.shop_score["seller_service"]["rank"] = self.get_score_rank(dsr_items[1])

        self.shop_score["logistics_quality"]["score"] = self.get_float(dsr_items[2].find_element_by_class_name("count").text)
        self.shop_score["logistics_quality"]["rank"] = self.get_score_rank(dsr_items[2])
        print("店铺评分：%s" % str(self.shop_score))

    @staticmethod
    def get_titles():
        titles = ["排名",
                  "店铺类型",
                  "商品",
                  "店名",
                  "链接",
                  "店铺资质",
                  "购买人数",
                  "价格-最低",
                  "价格-最高",
                  "促销价格-最低",
                  "促销价格-最高",
                  "店铺信用",
                  "收藏人数",
                  "宝贝与描述相符",
                  "宝贝与描述相符比同行平均水平",
                  "卖家的服务态度",
                  "卖家的服务态度比同行平均水平",
                  "物流服务的质量",
                  "物流服务的质量比同行平均水平",
                  "评价人数",
                  "追加评论",
                  "带图片评论",
                  "好评",
                  "中评",
                  "差评",
                  "邮费"]
        return titles

    @staticmethod
    def check_auth_code(driver, shop_url):
        # 由于流量问题，被要求输入验证码
        try:
            driver.find_element_by_id("checkcodeImg")
            driver.find_element_by_id("ks-stdmod-header-ks-component253")
            input("please_verify:")
            time.sleep(300)
            driver.get(shop_url)
            driver.refresh()
        except Exception as e:
            pass

    def get_all_attributes(self, all_commitments):
        raise NotImplemented
