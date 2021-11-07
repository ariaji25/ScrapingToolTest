from config import Config
from scraping import ScrapingTool


def main():
    # Write the exported csv header
    ScrapingTool().writeCsvHeader(fileName=Config().EXPORT_FILE_NAME)
    # Do a loop to extract the product according to many batches of parameters.
    # Each batch will get 15 data
    for i in range(1, Config().BATHC+1):
        ScrapingTool().extractProduct(i, batch=i)


if __name__ == "__main__":
    main()
