import arxiv
import os
from urllib.request import urlopen
from markdownify import markdownify as md

def agent_webscraping(url: str) -> str:
    try:
        page = urlopen(url)
        html: str = page.read().decode("utf-8")
        return md(html)
    except Exception as e:
        return f"[ERROR] Could not fetch the URL: {e}"



class ArxivConnector:
    def __init__(self):
        self.client = arxiv.Client()

    def search(self, subject: str, sort: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate, max_results: int = 5):
        search = arxiv.Search(
            query=subject,
            max_results=max_results,
            sort_by=sort
        )
        return self.client.results(search)

    def print_summaries(self, subject: str):
        for result in self.search(subject):
            print(f"Title: {result.title}")
            print(f"Summary: {result.summary}")
            print(f"Authors: {[a.name for a in result.authors]}")
            print(f"Published: {result.published}")
            print(f"PDF: {result.pdf_url}")
            print("="*80)

    def download_papers(self, subject: str, dirpath: str = "./downloads", max_results: int = 5):
        os.makedirs(dirpath, exist_ok=True)
        for result in self.search(subject, max_results=max_results):
            safe_title = "".join(c if c.isalnum() else "_" for c in result.title[:50])
            filename = f"{safe_title}.pdf"
            print(f"Downloading: {result.title}")
            result.download_pdf(dirpath=dirpath, filename=filename)
            print(f"Saved to: {os.path.join(dirpath, filename)}")


if __name__ == "__main__":
    x=agent_webscraping("https://mitchellh.com/writing/my-startup-banking-story")
    print(x)
