import requests

def get_citing_arxiv_ids(target_arxiv_id):
    """
    Takes an arXiv ID (e.g., '2106.15928'), finds all papers that cite it,
    and returns two lists: arXiv DOIs and non-arXiv DOIs of those citing papers.
    """
    # The Semantic Scholar API accepts "ARXIV:xxxx" as an ID directly
    paper_id = f"ARXIV:{target_arxiv_id}"
    
    # URL for the Semantic Scholar Graph API
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    
    # We ask for the 'citations' field, and specifically the 'externalIds' of those citations
    params = {
        "fields": "citations.externalIds,citations.title,citations.year"
    }

    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 404:
            return "Error: Paper not found. Check your arXiv ID."
        
        data = response.json()
        
        if "citations" not in data or not data["citations"]:
            return "No citations found."

        print(f"Found {len(data['citations'])} citing papers in total.")
        
        citing_arxiv_dois = set()
        citing_non_arxiv_dois = set()
        
        for citation in data["citations"]:
            external_ids = citation.get("externalIds", {})
            
            if "ArXiv" in external_ids:
                arxiv_id = external_ids["ArXiv"]
                arxiv_doi = f"10.48550/arXiv.{arxiv_id}"
                citing_arxiv_dois.add(arxiv_doi)
            elif "DOI" in external_ids and external_ids["DOI"]:
                citing_non_arxiv_dois.add(external_ids["DOI"])

        return sorted(citing_arxiv_dois), sorted(citing_non_arxiv_dois)

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    target_id = input("Enter the arXiv ID (e.g., 2106.15928): ").strip()

    if not target_id:
        print("No arXiv ID provided. Exiting.")
    else:
        results = get_citing_arxiv_ids(target_id)

        if isinstance(results, str):
            print(results)
        else:
            arxiv_dois, non_arxiv_dois = results

            with open("arxiv_doi.txt", "w", encoding="utf-8") as f_arxiv:
                for doi in arxiv_dois:
                    f_arxiv.write(doi + "\n")

            with open("non_arxiv_doi.txt", "w", encoding="utf-8") as f_non:
                for doi in non_arxiv_dois:
                    f_non.write(doi + "\n")

            print(f"\nSaved {len(arxiv_dois)} arXiv DOIs to arxiv_doi.txt")
            print(f"Saved {len(non_arxiv_dois)} non-arXiv DOIs to non_arxiv_doi.txt")

            # Quick preview of first few entries
            if arxiv_dois:
                print("\nSample arXiv DOIs:")
                for doi in arxiv_dois[:5]:
                    print(doi)

            if non_arxiv_dois:
                print("\nSample non-arXiv DOIs:")
                for doi in non_arxiv_dois[:5]:
                    print(doi)
