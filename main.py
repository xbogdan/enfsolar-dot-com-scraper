import argparse
from tqdm import tqdm

from utils import DetailPageScraper, read_input_from_csv, DetailPageParser, get_files_to_parse, write_report

# program parameters
arg_parser = argparse.ArgumentParser(description="enfsolar.com scraper")
arg_parser.add_argument('--csv-file', default=None, type=str, help="File path for .csv list with post codes.")
arg_parser.add_argument("--extract", action="store_true", help="Run the extractor.")
arg_parser.add_argument("--scrape", action="store_true", help="Run the scraper.")
args = arg_parser.parse_args()

if __name__ == '__main__':
    if args.scrape:
        urls = read_input_from_csv(args.csv_file)
        with DetailPageScraper() as scraper:
            for url in tqdm(urls):
                scraper.make_request(url)

    if args.extract:
        parser = DetailPageParser()
        files = get_files_to_parse()
        data = []
        for file_name in tqdm(files):
            with open(file_name, 'r') as file:
                data.append(parser.extract(file.read()))

        write_report(data)

