import requests
from bs4 import BeautifulSoup
headers = {
    "User-Agent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
}
## https://books.toscrape.com/catalogue/page-3.html

def getBookPrice():
    url = "https://books.toscrape.com"
    for index in range(1, 51):
        prefix = "/catalogue/page-"
        suffix = ".html"
        if index == 1:
            currentURL = url
        else:
            currentURL = url + prefix + str(index) + suffix
        content = requests.get(currentURL, headers=headers).text
        ## https://books.toscrape.com  https://www.hkp.com.hk/zh-hk/list/transaction
        ## print(content)
        soup = BeautifulSoup(content, "html.parser")
        all_information = soup.find_all("p", attrs={"class": "price_color"})
        for information in all_information:
            print(information.string[2:])

def getMovieName():
    url = "https://movie.douban.com/top250?start="
    suffix = "&filter="
    for index in range(0, 250, 25):
        newURL = url + str(index) + suffix
        content = requests.get(newURL, headers=headers).text
        soup = BeautifulSoup(content, "html.parser")
        names = soup.find_all("span", attrs={"class":"title"})
        ## https://movie.douban.com/top250?start=25&filter=
        ## https://movie.douban.com/top250?start=50&filter=
        ## https://movie.douban.com/top250?start=225&filter=
        for name in names:
            if "/" not in name.string:
                print(name.string)


getMovieName()

##
## #__next > main > div.sc-1xa3s3j-1.hBUjWI > div > div.rmc-tabs-content-wrap > div.rmc-tabs-pane-wrap.rmc-tabs-pane-wrap-active > div.difilq-3.ljLfya > div > div.infinite-scroll-component__outerdiv > div > div > div:nth-child(2) > div:nth-child(1)