# Harvard Art Museums Project – Multi-Classification & Streamlit Dashboard

This project fetches, organizes, and visualizes artifact data from the Harvard Art Museums public API for **five artwork classifications**. It leverages Streamlit for an interactive web dashboard and TiDB Cloud MySQL for robust data storage. The solution is scalable, modular, and ideal for both data analysis and public-facing applications.

## Features

- Fetches artifacts with images for five classifications from the Harvard Art Museums API (e.g., "Paintings", "Drawings", "Prints", "Coins", "Photographs")
- Organizes each artifact’s metadata, media details, and color analysis
- Loads all data into pre-defined MySQL tables on TiDB Cloud for easy querying and downstream use
- Efficient batch API and batch SQL insertions to handle large datasets
- Modern, responsive Streamlit UI for browsing, searching, and visualizing data

## Getting Started

1. **Clone the repository** and review dependencies (see requirements.txt).
2. **Get a Harvard Art Museums API key:** [API Signup](https://api.harvardartmuseums.org/).
3. **Set up TiDB Cloud MySQL schema**, or update connection settings as needed.
4. **Configure classifications:** Edit the classification list in the Streamlit script to target your chosen five (e.g., "Paintings", "Drawings", etc.).
5. **Run:**  

6. **Interact with the Streamlit UI** to filter, view, and analyze multi-classification art data.

## File Structure

- `HARVARD-S__STREAMLIT.py` — Main application for batch data ingest and Streamlit dashboard
- (Optional) `requirements.txt` — List of needed packages
- Generated CSVs (as needed by user tasks)

## Example Classifications Used

- Paintings
- Drawings
- Prints
- Coins
- Photographs

Change or expand the list within the `classification` list in your script to fetch and process new types.

## Typical Workflow

- User starts the Streamlit app
- For each classification:
 - Data is fetched from Harvard’s API (2,500+ items per class, with images)
 - Artifacts, media, and colors are extracted/organized
 - Batch inserts populate TiDB Cloud MySQL tables for efficient retrieval
- Streamlit UI presents tabular info, filtering, search, and simple analytics for all five categories

## License

[MIT](/LICENSE) (or your choice)

## Acknowledgements

- Built with the [Harvard Art Museums API](https://api.harvardartmuseums.org)
- Database powered by [TiDB Cloud](https://tidbcloud.com)
- UI powered by [Streamlit](https://streamlit.io)

---

**Explore, analyze, and visualize museum data across multiple Harvard Art Museum classifications—instantly and interactively!**

