class ProductData:
    def __init__(self, shop_name, product, shop_struct, shop_info):
        self.shop = shop_name
        self.product = product
        self.product_name_keys = product.lower().split(" ")
        self.shop_struct = shop_struct
        self.shop_info = shop_info
        self.url = self.__create_url()

    def __create_url(self):
        product_separated_name = self.product.replace(" ", self.shop_info["separator"])
        url = "{}{}".format(self.shop_info["request_url"], product_separated_name)
        if "extra_requests" in self.shop_info:
            url = "{}{}".format(url, self.shop_info["extra_requests"])
        return url
