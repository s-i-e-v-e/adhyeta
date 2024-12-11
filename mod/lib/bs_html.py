from bs4 import BeautifulSoup

def parse(html: str):
    soup = BeautifulSoup(html, 'lxml')
    return soup