import arxiv
import os
import tarfile

# Set your save directory ===
save_dir = "/Applications/AI Systems project Data/Latex_data"   #. set your local dirctory name
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
        # filename = f"{paper_id}_{title[:20]}.tar.gz"
        # filepath = os.path.join(save_dir, filename)
        tar_filename = f"{paper_id}_{title[:20]}.tar.gz"
        tar_path = os.path.join(save_dir, tar_filename)
        extract_dir = os.path.join(save_dir, f"{paper_id}_{title[:20]}")

        # Skip existing files
        if os.path.exists(extract_dir):
            print(f"Already exists: {extract_dir}")
            continue

        try:
            print(f"Downloading: {result.title}")
            result.download_source(filename=tar_path)

            # === Extract tar.gz directly ===

            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=extract_dir)

            print(f"Saved to: {extract_dir}\n")

            # remove the .tar.gz after extraction
            os.remove(tar_path)
        except Exception as e:
            print(f" Failed to download {result.title}: {e}\n")

print("All downloads complete!")
print(f"Files saved in: {os.path.abspath(save_dir)}")