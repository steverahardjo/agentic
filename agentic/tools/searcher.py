import arxiv
import os
from urllib.request import urlopen
from markdownify import markdownify as md


def agent_webscraping(url: str) -> str:
    """
    Fetch a webpage and convert its HTML content into Markdown text.

    Args:
        url (str): The webpage URL to scrape.

    Returns:
        str: The webpage content converted to Markdown. Returns an error message
        if fetching or decoding fails.
    """
    try:
        page = urlopen(url)
        html: str = page.read().decode("utf-8")
        return md(html)
    except Exception as e:
        return f"[ERROR] Could not fetch the URL: {e}"


class ArxivConnector:
    """A simple connector to search, summarize, and download academic papers from arXiv."""

    def __init__(self):
        """Initialize the arXiv API client."""
        self.client = arxiv.Client()

    def search(
        self,
        subject: str,
        sort: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate,
        max_results: int = 5,
    ):
        """
        Search arXiv for papers by keyword or topic.

        Args:
            subject (str): The keyword or topic to search for.
            sort (arxiv.SortCriterion): Sorting option (default: by submission date).
            max_results (int): Maximum number of results to retrieve (default: 5).

        Returns:
            generator: Iterator yielding arxiv.Result objects.
        """
        search = arxiv.Search(
            query=subject,
            max_results=max_results,
            sort_by=sort
        )
        return self.client.results(search)

    def print_summaries(self, subject: str):
        """
        Print a readable list of paper summaries for a given search.

        Args:
            subject (str): Search keyword or topic.
        """
        for result in self.search(subject):
            print(f"Title: {result.title}")
            print(f"Summary: {result.summary}")
            print(f"Authors: {[a.name for a in result.authors]}")
            print(f"Published: {result.published}")
            print(f"PDF: {result.pdf_url}")
            print("=" * 80)

    def download_papers(self, subject: str, dirpath: str = "./downloads", max_results: int = 5):
        """
        Download PDFs of papers found on arXiv for a given topic.

        Args:
            subject (str): Topic or keyword to search for.
            dirpath (str): Directory path to save papers (default: ./downloads).
            max_results (int): Number of papers to download (default: 5).
        """
        os.makedirs(dirpath, exist_ok=True)

        for result in self.search(subject, max_results=max_results):
            # Sanitize file name (limit to 50 chars, replace special chars)
            safe_title = "".join(c if c.isalnum() else "_" for c in result.title[:50])
            filename = f"{safe_title}.pdf"

            print(f"Downloading: {result.title}")
            result.download_pdf(dirpath=dirpath, filename=filename)
            print(f"Saved to: {os.path.join(dirpath, filename)}")


if __name__ == "__main__":
    # Example usage: scrape a blog and print as Markdown
    x = agent_webscraping("https://mitchellh.com/writing/my-startup-banking-story")
    print(x)
