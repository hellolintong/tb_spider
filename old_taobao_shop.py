import time
import re
from taobao_shop import TbShop


class OldTbShop(TbShop):

    def __init__(self, query, rank, postage, url):
        super(OldTbShop, self).__init__(query, rank, postage, url)

    def get_shop_name(self, driver):
        self.shop_name = driver.find_element_by_class_name("shop-name-link").text
        print(self.shop_name)

    def get_shop_qualification(self, driver):
        try:
            driver.find_element_by_xpath("//a[@class='J_TGoldlog jinpai-v']")
            self.shop_qualification = "golden_shop"
            print("店铺资质：%s" % self.shop_qualification)
        except Exception as e:
            self.shop_qualification = ""
            print("店铺资质：%s" % self.shop_qualification)

    def get_shop_ranker(self, driver):
        driver.get(driver.find_element_by_class_name("shop-rank").find_element_by_tag_name("a").get_attribute("href"))
        try:
            driver.find_element_by_xpath("//a[@class='sufei-tb-dialog-close sufei-tb-overlay-close']").click()
        except Exception as e:
            pass
        text = driver.find_element_by_class_name("sep").find_elements_by_tag_name("li")[0].text
        self.shop_ranker = re.findall(r'\d+', text)[0]
        self.get_shop_score(driver)
        time.sleep(3)
        driver.back()
        driver.refresh()

    def get_comment(self, driver):

        def get_count(review_detail):
            return int(re.findall(r'\d+', review_detail.find_element_by_class_name("tb-tbcr-num").find_element_by_tag_name("span").text)[0])

        self.review_count = int(driver.find_element_by_class_name("J_ReviewsCount").text)
        driver.find_element_by_id("J_TabBar").find_elements_by_tag_name("li")[1].find_element_by_tag_name("a").click()
        time.sleep(1)
        review_details = driver.find_element_by_class_name("kg-rate-wd-filter-bar").find_elements_by_tag_name("li")
        self.review_with_good_count = get_count(review_details[1])
        self.review_with_normal_count = get_count(review_details[2])
        self.review_with_bad_count = get_count(review_details[3])
        print("评论总数：%d" % self.review_count)
        print("带好评数：%d" % self.review_with_good_count)
        print("带中评数：%d" % self.review_with_normal_count)
        print("带差评数：%d" % self.review_with_bad_count)

