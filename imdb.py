import requests
from bs4 import BeautifulSoup
from cookie import cookie
from loguru import logger
import pandas as pd
from statistics import stdev
import colorful as cf
import fire


header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52",
    "content-language": "eg-US",
    "cookie": cookie
}


def request_imdb(url: str, header: dict):
    res = requests.get(url, headers=header, timeout=2)
    if res.status_code == requests.codes.ok:
        # logger.debug("request successful!")
        pass
    else:
        logger.error("request failed!")
    return res


def parse_review(res) -> pd.DataFrame:
    global soup
    titles, rates = [], []
    soup = BeautifulSoup(res.text, 'html.parser')
    for row in soup.find_all("a", class_="title"):
        titles.append(row.get_text(strip=True))
    for row in soup.find_all("div", class_="ipl-ratings-bar"):
        rates.append(int(row.find("span", class_=None).text))

    # <div class="actions text-muted"> 21 out of 28 found this helpful.

    titleRate = dict(zip(titles, rates))
    df = pd.DataFrame(titleRate.items(), columns=["Title", "Rate"])
    return df


def main(code: str):
    url = f"https://www.imdb.com/title/{code}/reviews?sort=reviewVolume&dir=desc&ratingFilter=0"
    res = request_imdb(url, header)
    df = parse_review(res)
    describe = {}
    describe['Film'] = soup.find(
        "meta", attrs={"property": "og:title"}).get("content")
    # Drop 1 ?
    describe['Average useful score'] = df[df['Rate']
                                          != 0]['Rate'].mean().round(2)
    for k, v in describe.items():
        print(f"{k}: {cf.bold_coral(v)}")
    print(
        f"Standard Deviation: {cf.bold_coral(round(stdev(df['Rate'].tolist()), 2))}")
    print(df.to_markdown(index=False))


if __name__ == "__main__":
    fire.Fire(main)
