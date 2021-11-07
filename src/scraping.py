import requests
from bs4 import BeautifulSoup
import re
import csv

from config import Config


class ScrapingTool:

    def __init__(self) -> None:
        pass

    def getContent(self, page=1):
        # URL request to get proudcts with mobile category
        res = requests.get('https://www.tokopedia.com/search?ob=5&rt=4%2C5&sc=24&st=product&q=HP&page={}'.format(page), headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'ect': '4g',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
        })
        return res.text

    def getProductDetail(self, url):
        # URL request to get proudcts detail with 
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'ect': '4g',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': 'macOS',
            'Upgrade-Insecure-Requests': '1'
        }, allow_redirects=False)
        return res.text

    # Function to extract the product description from product detail page that have loaded with `getProductDetail()`
    def extractProductDetail(self, url):
        prodcut_description = ''
        detail_content = self.getProductDetail(url)
        parsed_html = BeautifulSoup(detail_content, 'html.parser')
        for item in parsed_html.findAll(
                'div', {'data-testid': 'lblPDPDescriptionProduk'}):
            prodcut_description = (str(item).replace(
                '<div data-testid="lblPDPDescriptionProduk">', '').replace('<br/>', '\n').replace('amp;', ' ').replace('</div>', ''))
        return prodcut_description

    def extractProduct(self, page=1, batch=1, fileName=Config().EXPORT_FILE_NAME):
        raw_html = self.getContent(page=page)
        parsed_html = BeautifulSoup(raw_html, 'html.parser')
        productName = []
        productPrice = []
        productRating = []
        productStore = []
        productImage = []
        productLink = []
        productDesc = []

        # Find products name
        for item in parsed_html.findAll(
                'div', {'data-testid': 'spnSRPProdName'}):
            productName.append(str(item).split('>')[1].replace('</div', ''))

        # Find products images
        for item in parsed_html.findAll(
                'div', {'data-testid': 'imgSRPProdMain'}):
            # print(item)
            productImage.append(str(item).split('src="')[
                                1].replace('" title=""/></div>', ''))

        # Find products url to get det descriptions
        for item in parsed_html.findAll(
                'a', {'class': 'pcv3__info-content css-1qnnuob'}):
            link = str(item).split('"')[3]
            if link.find('r=') != -1:
                productLink.append(str(link).split('r=')[1].split(";")[0].replace('%3A', ':').replace(
                    '%2F', '/').replace('%3F', '?').replace('%3D', '=').replace('&amp', ''))
            else:
                productLink.append(str(item).split('"')[3])

        # Find products price
        for item in parsed_html.findAll(
                'div', {'data-testid': 'spnSRPProdPrice'}):
            productPrice.append(str(item).split('>')[1].replace('</div', ''))

        # Find products rating
        for item in parsed_html.findAll(
                'span', {'class': 'css-etd83i'}):
            productRating.append(str(item).split('>')[1].replace('</span', ''))

        # Find products store
        products_store = parsed_html.findAll(
            'span', {'class': 'css-qjiozs flip'})
        rangeI = int(len(products_store)/2)
        for i in range(rangeI):
            store = '{}, {}'.format(str(products_store[i+(i+1)]).split('>')[1].replace(
                '</span', ''), str(products_store[i+i]).split('>')[1].replace('</span', ''))
            productStore.append(store)

        # Get products descriptions
        for p_link in productLink:
            p_desc = self.extractProductDetail(str(p_link))
            productDesc.append(p_desc)

        # Check the data is in the same length
        # At the first page of data product description and rating have different value
        # because it contains the promotion product
        if len(productDesc) > len(productName):
            diff = len(productDesc) - len(productName)
            productDesc = productDesc[diff:len(productDesc)]

        if len(productRating) > len(productName):
            diff = len(productRating) - len(productName)
            productRating = productRating[diff:len(productDesc)]

        # Export the products to csv file
        csv_index_count = ((batch-1) * 15) + 1
        for i in range(len(productName)):
            def p_name(i): return productName[i] if i < len(
                productName) else ''

            def p_desc(i): return productDesc[i] if i < len(
                productDesc) else ''

            def p_store(i): return productStore[i] if i < len(
                productStore) else ''

            def p_price(i): return productPrice[i] if i < len(
                productPrice) else ''

            def p_rating(i): return productRating[i] if i < len(
                productRating) else ''
            def p_image(i): return productImage[i] if i < len(
                productName) else ''

            self.exportToCSV([csv_index_count, p_name(i), p_desc(i), p_store(i),
                             p_price(i), p_rating(i), p_image(i)], fileName=fileName)
            csv_index_count+=1
        print('{} product has been stored to {}'.format(csv_index_count, fileName))

    def writeCsvHeader(self, fileName):
        header = ['No', 'NAME', 'Description',
                  'Store', 'Price', 'Rating', 'Image URL']
        with open('./export/{}'.format(fileName), 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    def exportToCSV(self, row, fileName):
        with open('./export/{}'.format(fileName), 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
