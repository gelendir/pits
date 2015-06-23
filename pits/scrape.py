import click
import json
import os
import requests
import logging

from bs4 import BeautifulSoup

MUTOPIA_URL = "http://www.mutopiaproject.org"


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    level = logging.DEBUG if debug else logging.INFO
    requests_level = logging.DEBUG if debug else logging.WARN
    logging.basicConfig(level=level)
    logging.getLogger('requests').setLevel(requests_level)


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--output', '-o', default='catalog.json', type=click.Path())
@click.option('--merge', '-m', type=click.Path(exists=True))
def scrape(filepath, output, merge):
    pieces = tuple(scrape_catalog(filepath))
    catalog = {'catalog': pieces,
               'whitelist': []}

    if merge:
        with open(merge) as f:
            catalog.update(json.loads(f.read()))

    with open(output, 'w') as f:
        f.write(json.dumps(catalog, indent=4, separators=(',', ': ')))


def scrape_catalog(filepath):
    with open(filepath) as f:
        soup = BeautifulSoup(f.read())

    for row in soup.find_all('tr', recursive=False):
        cells = row.table('td')
        info = extract_info(cells)
        yield info


def extract_info(cells):
    lines = dict(enumerate(cells))

    ly = lines[12].a['href'].lstrip('.')
    parts = ly.split('/')
    short_author, short_title = parts[2], parts[-1].rstrip('lyzip').rstrip('.')

    return {
        'title': lines[0].text,
        'short_title': short_title,
        'author': lines[1].text,
        'short_author': short_author,
        'instrument': lines[4].text,
        'ly': ly,
        'midi': lines[13].a['href'].lstrip('.'),
    }


@cli.command()
@click.argument('catalogpath', type=click.Path(exists=True))
@click.option('--output', '-o', default='scores', type=click.Path())
def download(catalogpath, output):
    if not os.path.exists(output):
        os.mkdir(output)

    with open(catalogpath) as f:
        catalog = json.loads(f.read())

    for score in catalog['catalog']:
        download_score(score, output)


def download_score(score, output):
    logging.info("downloading %s", score['title'])

    path = os.path.join(output, score['short_author'], score['short_title'])
    if not os.path.exists(path):
        os.makedirs(path)

    download_file(path, score['ly'])
    download_file(path, score['midi'])

    with open(os.path.join(path, 'metadata.json'), 'w') as f:
        f.write(json.dumps(score))


def download_file(path, url):
    filename = os.path.basename(url)
    full_url = "{}/{}".format(MUTOPIA_URL, url)
    filepath = os.path.join(path, filename)

    if os.path.exists(filepath):
        logging.debug("%s exists, skipping", filepath)
        return

    logging.debug("downloading %s", full_url)
    response = requests.get(full_url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        logging.error("Could not download %s %s %s",
                      full_url,
                      response.status_code,
                      response.text)


def main():
    cli()


if __name__ == "__main__":
    main()
