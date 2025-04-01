from bs4 import BeautifulSoup
from parsel import Selector

class NoteContent:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    detail_link: str = ""

    def __str__(self):
        return f"""
        Title: {self.title}
        User: {self.author}
        Publish Date: {self.publish_date}
        Detail Link: {self.detail_link}        
        """

def parse_html_use_bs(html_content: str):
    notecontent = NoteContent()
    soup = BeautifulSoup(html_content, "lxml")
    notecontent.title = soup.select("div.r-ent div.title a")[0].text.strip()
    notecontent.author = soup.select("div.r-ent div.meta div.author")[0].text.strip()
    notecontent.publish_date = soup.select("div.r-ent div.meta div.date")[0].text.strip()
    notecontent.detail_link = soup.select("div.r-ent div.title a")[0]["href"]
    print("Beautiful" + "*" * 30)
    print(notecontent)
    print("Beautiful" + "*" * 30)

