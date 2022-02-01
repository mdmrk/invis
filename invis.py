import re
import asyncio
import aiohttp
import hashlib
from nostril import nonsense
from selenium import webdriver as webdriver
from enum import Enum
from bs4 import BeautifulSoup


URL_NEWS_LETTER = "https://www.getrevue.co/profile/Forocoches"
EXCHANGE = "https://www.forocoches.com/codigo/"


class InviType(Enum):
    UNDERSCORE = 0,
    DOT = 1,
    VOID = 2


class FirefoxDriver():
    def __init__(self):
        self.driver = None

    def init(self):
        self.driver = webdriver.Firefox(executable_path="./firefox_driver")

    def open(self):
        self.driver.get(EXCHANGE)

    def fill(self, invis: [str]):
        if len(invis):
            self.driver.find_element_by_name("codigo").send_keys(invis[0])


def get_hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


async def get_web_page(session, url: str):
    async with session.get(url) as r:
        return await r.text()


def get_upper_lower(strings: [str]) -> bool:
    for string in strings:
        if re.search(r"MAY[UÚ]S|MIN[UÚ]S", string.text.upper()):
            return True
    return False


def upper_lower(string: str):
    res = ""

    for char in string:
        if re.search(r"[A-Z]", char):
            res += char.lower()
        elif re.search(r"[a-z]", char):
            res += char.upper()
        elif re.search(r"\d", char):
            res += char
    return res


def get_operation(strings: [str]) -> int:
    op = 0

    for string in strings:
        if re.search(r"\+1", string.text):
            op = 1
        elif re.search(r"-1", string.text):
            op = -1
    return op


def operate(string: str, number: int):
    invi = ""

    for char in string:
        if re.search(r"[0-9]", char):
            invi += str(int(char) + number)
        else:
            invi += char
    return re.sub(r"[\W_]", "", invi).strip()


def extract_invi_from_str(pattern: str, string: str, type: InviType, soup: BeautifulSoup) -> [str]:
    content = soup.find_all("div", "revue-p")
    matches = re.finditer(pattern, string)
    number = get_operation(content)
    ul = get_upper_lower(content)
    invis = []

    if type == InviType.UNDERSCORE:
        for match in matches:
            invis.append(operate(match.group(0), number))
    elif type == InviType.DOT:
        for match in matches:
            invis.append(operate(match.group(0), number))
    elif type == InviType.VOID:
        for match in matches:
            match = match.group(0)

            try:
                if nonsense(match):
                    if ul:
                        invis.append(upper_lower(match))
                    else:
                        invis.append(match)
            except Exception:
                pass
    return invis


def output_invis(invis: [str]):
    res = ""

    for invi in invis:
        res += invi + "\n\n"
    with open("invis.txt", "w") as o:
        o.write(res)
    o.close()


async def get_invis(session, url: str, soup: BeautifulSoup):
    post_raw = await get_web_page(session, url)
    invis = []

    invis.extend(extract_invi_from_str(
        r"(\w_){5,}\w", post_raw, InviType.UNDERSCORE, soup))
    invis.extend(extract_invi_from_str(
        r"(\w\.){5,}\w", post_raw, InviType.DOT, soup))
    invis.extend(extract_invi_from_str(
        r"\b[\w\d]{9}\b", post_raw, InviType.VOID, soup))
    return invis


async def detect_news_letter_update(session):
    old_hash = get_hash(str(BeautifulSoup(await get_web_page(session, URL_NEWS_LETTER), "html.parser").find_all("a", "issue-cover")))

    while True:
        news_letter_raw = await get_web_page(session, URL_NEWS_LETTER)
        news_letter_bs = BeautifulSoup(news_letter_raw, "html.parser")
        posts = news_letter_bs.find_all("a", "issue-cover")
        new_hash = get_hash(str(posts))

        if new_hash == old_hash:
            continue
        if not len(posts):
            continue
        new_post_url = posts[0]["href"]
        return await get_invis(session, "https://www.getrevue.co" + new_post_url, news_letter_bs)


async def main():
    url = "https://www.getrevue.co/profile/Forocoches/issues/esta-semana-en-forocoches-publicacion-30-752589"
    driver = FirefoxDriver()

    async with aiohttp.ClientSession() as session:
        invis = await get_invis(session, url, BeautifulSoup(await get_web_page(session, url), "html.parser"))
        # invis = await detect_news_letter_update(session)
        output_invis(invis)
        driver.init()
        driver.open()
        driver.fill(invis)


if __name__ == "__main__":
    asyncio.run(main())
