# Necessary Imports
from bs4 import BeautifulSoup
from scrapy import Field, Item
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


# Item to store crawled data
class FeatureItem(Item):
    url = Field()  # url of the element extracted
    referrer_url = Field()  # url which was crawled before the current url
    data_source = Field()  # source of data (html/pdf/etc.) for extensibility
    product_line = Field()  # name of the product line (e.g.: Quip, Service Cloud, Sales Cloud...)
    feature_name = Field()  # relative depth of the item (e.g.: depth of div(in parsed html) or table of content level (aria-level))
    feature_description = Field()  # extracted text without processing and cleansing


# Crawler to extract product related (marketing) pages from https://www.salesforce.com/products
class SFSiteCrawler(CrawlSpider):
    name = "sfsitecrawler"  # Spider name
    custom_settings = {
        'DEPTH_LIMIT': '5'
    }
    allowed_domains = ["www.salesforce.com"]  # Which (sub-)domains shall be scraped?
    start_urls = ["https://www.salesforce.com/editions-pricing/overview/"]  # Start from products
    rules = [
        Rule(LinkExtractor(allow='/editions-pricing'),  # allow only pricing related sites
             callback='parse_item', follow=True)]

    # Parse product related pages
    def parse_item(self, response):

        # xpath selector to check if pricing information present
        pricing_tables = response.xpath(
            #'//div[@class=\'row row-relative pricing-feature table-row\']//div[@class=\'vert-center-child\']/span[@class=\'feature-text\']/..')
            '//div[@class=\'vert-center-child\']/span[@class=\'feature-text\']/..')

     
        # check if page has feature table -
        # not all pages contain the table (we might be on a higher level and need to crawl further)
        if pricing_tables is not None:
            count = 0
            for row in pricing_tables:
                print(row)
                feature = FeatureItem()
                feature['url'] = response.url #set items url
                feature['referrer_url'] = response.request.headers.get('Referer', None) #store referrer
                #get the product line of the feature
                product_line = response.xpath('//div[@class=\'headingComponent parbase section\']/h1/span/text()')\
                               .get().rsplit(' ',1)[0].strip()

                #store feature name
                feature_name = row.xpath('./span[@class=\'feature-text\']/text()').get()
                #store feature description. Not every feature has a description so check the presence otherwise N/A
                try:
                    feature_description = \
                    row.xpath('./span[@class=\'text-cirrus tooltip-enabled icon-sfdc-icon-tooltip\']').attrib[
                        'aria-label']
                    feature['feature_description'] = feature_description
                except:
                    feature['feature_description'] = ''
                #set the datasource
                feature['data_source'] = 'html'
                feature['feature_name'] = feature_name
                feature['product_line'] = product_line
                yield feature   




#                     feature = FeatureItem()
#                     feature['url'] = response.url
#                     feature['referrer_url'] = response.request.headers.get('Referer', None)
#                     feature['data_source'] = 'html'
#                     feature['feature_name'] = feature.xpath('//span[@id=\'feature-text\']').get()
#                     feature['feature_description'] = feature.xpath('//span[@id=\'text-cirrus tooltip-enabled icon-sfdc-icon-tooltip\']').get()
#
#                     yield feature
#
