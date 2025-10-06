import arxiv
import os

# Set your save directory ===
save_dir = ""   #. set your local dirctory name
os.makedirs(save_dir, exist_ok=True)

# Define search queries and number of results ===
queries = ["cat:cs.LG", "cat:cs.CV", "cat:cs.AI", "cat:stat.ML", "cat:math.AG"]
# queries = ["cat:cs.LG"]
max_results_per_query = 100

# Download papers ===
for query in queries:
    print(f"Fetching papers for query: '{query}'\n")

    search = arxiv.Search(
        query=query,
        max_results=max_results_per_query,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    for result in search.results():
        # Clean filename (limit to 50 chars)
        paper_id = result.get_short_id()
        title = result.title.replace(" ", "_").replace("/", "_")
        filename = f"{paper_id}_{title[:20]}.pdf"
        filepath = os.path.join(save_dir, filename)

        # Skip existing files
        if os.path.exists(filepath):
            print(f"Already exists: {filename}")
            continue

        try:
            print(f"Downloading: {result.title}")
            result.download_pdf(filename=filepath)
            print(f"Saved to: {filepath}\n")
        except Exception as e:
            print(f" Failed to download {result.title}: {e}\n")

print("All downloads complete!")
print(f"Files saved in: {os.path.abspath(save_dir)}")