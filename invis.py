import re
import asyncio
import hashlib
from enum import Enum
from time import sleep
from nostril import nonsense
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import random


URL_NEWS_LETTER = "https://www.getrevue.co/profile/Forocoches"
EXCHANGE = "https://www.forocoches.com/codigo/"


class InviType(Enum):
    UNDERSCORE = 0,
    DOT = 1,
    VOID = 2,
    WHITESPACE = 3


def get_hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


async def get_web_page(session, url: str) -> str:
    async with session.get(url) as r:
        return await r.text()


def get_upper_lower(post_content: str) -> bool:
    if re.search(r"MAY[UÚ]S|MIN[UÚ]S", post_content.upper()):
        return True
    return False


def upper_lower(string: str) -> str:
    res = ""

    for char in string:
        if re.search(r"[A-Z]", char):
            res += char.lower()
        elif re.search(r"[a-z]", char):
            res += char.upper()
        elif re.search(r"\d", char):
            res += char
    return res


def get_operation(post_content: str) -> int:
    op = 0
    add = re.search(r"\+([0-9])", post_content)
    sub = re.search(r"-([0-9])", post_content)

    if add:
        op = int(add.group(1))
    elif sub:
        op = -int(sub.group(1))
    return op


def operate(string: str, operation: int) -> str:
    invi = ""

    for char in string:
        if re.search(r"[0-9]", char):
            invi += str(int(char) + operation)
        else:
            invi += char
    return re.sub(r"[\W_]", "", invi).strip()


def spelled_numbers(string: str) -> str:
    return string.replace("(CERO)", "0").replace("(UNO)", "1").replace("(DOS)", "2").replace("(TRES)", "3").replace("(CUATRO)", "4").replace("(CINCO)", "5").replace("(SEIS)", "6").replace("(SIETE)", "7").replace("(OCHO)", "8").replace("(NUEVE)", "9")


def scrap_invis(pattern: str, string: str, operation: int, requires_upper_lower: bool, type: InviType):
    matches = re.finditer(pattern, string)
    invis = []

    if type == InviType.UNDERSCORE:
        for match in matches:
            invis.append(operate(spelled_numbers(match.group(0)), operation))
    elif type == InviType.DOT:
        for match in matches:
            invis.append(operate(spelled_numbers(match.group(0)), operation))
    elif type == InviType.VOID:
        for match in matches:
            match = match.group(0)

            try:
                if nonsense(match):
                    if requires_upper_lower:
                        invis.append(upper_lower(match))
                    else:
                        invis.append(match)
            except Exception:
                pass
    return invis


def output_invis(invis):
    res = ""

    for invi in invis:
        res += f"{invi}\n\n"
    try:
        with open("invis.txt", "w") as o:
            o.write(res)
        o.close()
        print("[!] LAS INVIS ESTÁN EN EL FICHERO 'invis.txt'")
        print("\nInvis:")
        print(res)
    except OSError:
        print(
            f"Error al escribir invis al archivo... mostrando por pantalla\n\n{res}")


async def get_invis(session: ClientSession, url: str):
    post_raw = await get_web_page(session, url)
    post_bs = BeautifulSoup(post_raw, "html.parser")
    post_content = str(post_bs.find_all("div", "revue-p"))
    operation = get_operation(post_content)
    requires_upper_lower = get_upper_lower(post_content)
    invis = []

    invis.extend(scrap_invis(
        r"(\w_){5,}\w", post_content, operation, requires_upper_lower, InviType.UNDERSCORE))
    invis.extend(scrap_invis(
        r"(\w\.){5,}\w", post_content, operation, requires_upper_lower, InviType.DOT))
    invis.extend(scrap_invis(
        r"\b[\w\d]{9}\b", post_content, operation, requires_upper_lower, InviType.VOID))
    invis.extend(scrap_invis(
        r"(\w\s){5,}\w", post_content, operation, requires_upper_lower, InviType.WHITESPACE))
    return invis


async def detect_news_letter_update(session: ClientSession) -> str:
    old_hash = get_hash(str(BeautifulSoup(await get_web_page(session, URL_NEWS_LETTER), "html.parser").find_all("a", "issue-cover")))

    while True:
        sleep(random.uniform(12, 16))
        news_letter_raw = await get_web_page(session, URL_NEWS_LETTER)
        news_letter_bs = BeautifulSoup(news_letter_raw, "html.parser")
        posts = news_letter_bs.find_all("a", "issue-cover")
        new_hash = get_hash(str(posts))

        if new_hash == old_hash:
            continue
        print("[!] NUEVO POST\n" * 10)
        new_post_url = posts[0]["href"]
        new_post_full_url = "https://www.getrevue.co" + new_post_url
        print(new_post_full_url, "\n")
        return new_post_full_url


async def main():
    async with ClientSession() as session:
        new_post_url = await detect_news_letter_update(session)
        invis = await get_invis(session, new_post_url)
        if len(invis):
            print("[!] SE HAN ENCONTRADO INVIS")
            output_invis(invis)
        else:
            print(
                f"No se han encontrado invis... prueba a buscar tú manualmente:\n{new_post_url}")


if __name__ == "__main__":
    asyncio.run(main())
