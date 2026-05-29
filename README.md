# AI Literature Research Feed Automation

A local-first, AI-assisted scientific literature monitoring pipeline for collecting, ranking, summarizing, and exporting research papers. The project is designed for researchers who want an automated literature feed focused on materials science, battery research, polymer-derived ceramics, SiOC, hard carbon, and related topics.

The system can run locally with Python, expose a FastAPI endpoint for automation, and integrate with n8n for scheduled email digests. It supports local LLM summarization through Ollama and can export citation files for tools such as Zotero, Mendeley, EndNote, and JabRef.

---

## Features

### Literature Collection

The pipeline can search multiple scientific sources:

- Crossref
- OpenAlex
- Semantic Scholar
- arXiv

Search terms are configurable in `config/interests.yaml`.

### Research-Focused Ranking

Collected papers are ranked using domain-specific logic. The default configuration prioritizes topics such as:

- SiOC battery and anode materials
- Polymer-derived ceramics
- Hard carbon for battery applications
- Lithium-ion and sodium-ion battery research
- Materials science publications related to energy storage

The ranking rules can be adjusted to match a different research domain.

### AI Summarization

The project can generate AI-assisted summaries of selected papers using:

- local Ollama models
- optional OpenAI-compatible providers, if configured

Summaries are saved as Markdown digests and can be sent through n8n workflows.

### Citation Export

The pipeline exports selected papers as:

- BibTeX
- RIS
- Markdown digest
- JSONL archive

These outputs are useful for reference managers, dashboards, and downstream literature analysis.

### Automation with n8n

n8n can be used to:

- trigger the feed on a schedule
- call the FastAPI endpoint
- read generated output files
- send email digests
- attach BibTeX and RIS files

---

## System Architecture

```text
Crossref / Semantic Scholar / arXiv
                  ↓
        Literature Collection
                  ↓
         Ranking + Filtering
                  ↓
      Ollama AI Summarization
                  ↓
 BibTeX / RIS / Markdown Export
                  ↓
          FastAPI Endpoint
                  ↓
          n8n Automation
                  ↓
        Email Digest Delivery
```

## Project Structure

```text
.
|-- api.py
|-- run_feed.py
|-- requirements.txt
|-- Dockerfile
|-- docker-compose.yml
|-- docker-compose.api-only.yml
|-- .env.example
|-- .gitignore
|-- .dockerignore
|-- config/
|   `-- interests.yaml
|-- data/
|   |-- bibtex/
|   |-- digests/
|   |-- feeds/
|   |-- logs/
|   `-- ris/
|-- docs/
|   `-- screenshots/
|-- n8n/
|   `-- node_parameters.md
`-- scripts/
    |-- config_loader.py
    |-- fetch_sources.py
    |-- rank_and_export.py
    `-- utils.py
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a Python Environment

Use any standard Python environment manager, for example `venv`, `conda`, or `pyenv`.

Example using `venv`:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if needed.

The project can run without paid API keys. Semantic Scholar may provide higher rate limits if an API key is added, and OpenAlex can use an optional contact email (`OPENALEX_MAILTO`) for polite API usage.

### Semantic Scholar API Notes

Semantic Scholar can be used without a key, but anonymous requests share public rate limits and may return HTTP `429`. For more reliable scheduled feeds, request a free Semantic Scholar API key and set it in `.env`:

```env
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key
```

The feed respects Semantic Scholar's introductory limit of about **1 request/second**. Keep `max_results_per_keyword` modest for scheduled runs. Recommended settings:

```text
10-15 records/keyword = normal scheduled feed
20-25 records/keyword = broader check
50+ records/keyword = avoid for frequent scheduled runs unless you know your rate plan allows it
```

OpenAlex and Crossref are the preferred primary discovery sources. Semantic Scholar is most useful for abstracts, citation counts, and extra coverage when the API is available.

### 5. Configure Research Interests

Edit:

```text
config/interests.yaml
```

Example:

```yaml
keywords:
  - "SiOC anode"
  - "polymer derived ceramic battery"
  - "hard carbon sodium ion battery"

exclude_keywords:
  - "unrelated"
  - "medical"
  - "clinical"

max_results_per_keyword: 20
min_relevance_score: 0
```

### 6. Run the Feed Locally

```bash
python run_feed.py
```

Generated outputs will be saved under:

```text
data/
|-- bibtex/
|-- digests/
|-- feeds/
`-- ris/
```

---

## Running with FastAPI

Start the API server:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Check that the API is running:

```bash
curl http://localhost:8000/health
```

Run the feed through the API:

```bash
curl -X POST http://localhost:8000/run_feed
```

The API mode is useful when connecting the project to n8n or another automation tool.

---

## Running with Docker Compose

A production-oriented Docker Compose file is included.

Build and start the default services:

```bash
docker compose up -d --build
```

This starts the API and n8n services.

Check containers:

```bash
docker compose ps
```

Stop the stack:

```bash
docker compose down
```

### API-only Docker Mode

If you already run n8n separately, use:

```bash
docker compose -f docker-compose.api-only.yml up -d --build
```

This starts only the API service.

---

## Ollama Support

The project can use a local Ollama model for summarization.

Install Ollama from the official website, then pull a model, for example:

```bash
ollama pull llama3.2:3b
```

Set the model name in `.env`:

```env
OLLAMA_MODEL=llama3.2:3b
```

If Ollama is running on the host machine and the API is running in Docker, use a host-accessible Ollama URL in `.env`.

If you want Docker Compose to start an Ollama container, use the optional Ollama profile:

```bash
docker compose --profile ollama up -d --build
```

Then pull a model inside the Ollama container:

```bash
docker exec -it literature-ollama ollama pull llama3.2:3b
```

---

## n8n Integration

The n8n workflow can call the FastAPI endpoint and read generated files from the mounted output folder.

Typical workflow:

```text
Schedule Trigger
    ->
HTTP Request to /run_feed
    ->
Select generated outputs
    ->
Read BibTeX / RIS / Markdown digest files
    ->
Send email digest
```

### n8n Workflow Screenshot

![n8n workflow overview](docs/screenshots/n8n_workflow_overview.png)

Example file paths inside the n8n container:

```text
/home/node/.n8n-files/bibtex/<file>.bib
/home/node/.n8n-files/ris/<file>.ris
/home/node/.n8n-files/digests/<file>.md
/home/node/.n8n-files/feeds/<file>.jsonl
```

Example n8n expression for a BibTeX attachment:

```text
=/home/node/.n8n-files/bibtex/{{$("Papers selection").first().json.outputs.bibtex.split('/').pop()}}
```

Example n8n expression for a RIS attachment:

```text
=/home/node/.n8n-files/ris/{{$("Papers selection").first().json.outputs.ris.split('/').pop()}}
```

More n8n node details are provided in:

```text
n8n/node_parameters.md
```

---

## Output Files

After a successful run, the pipeline may generate:

```text
data/feeds/papers.jsonl
data/digests/latest_digest.md
data/bibtex/selected_papers.bib
data/ris/selected_papers.ris
```

Exact filenames may vary depending on timestamped exports or workflow configuration.

---

## Example Use Cases

- Monitor new papers in a specific research field
- Generate weekly or daily scientific literature digests
- Export selected papers to Zotero or Mendeley
- Build a local research feed for a PhD or postdoctoral project
- Prepare a dataset for a literature dashboard or RAG assistant
- Automate research updates with n8n

---

## GitHub Notes

Do not commit private or generated local files such as:

```text
.env
.n8n/
.ollama/
data/**/*.jsonl
data/**/*.bib
data/**/*.ris
data/**/*.md
data/logs/*
data/pdfs/*
```

Use `.env.example` to document required environment variables.

Use `.gitkeep` files to preserve empty output folders in Git.

Recommended screenshot location:

```text
docs/screenshots/
```

Suggested screenshots:

```text
docs/screenshots/n8n_workflow_overview.png
docs/screenshots/email_example.png
docs/screenshots/digest_file_example.png
docs/screenshots/bib_file_example.png
```

Avoid screenshots that expose API keys, personal emails, private folders, or credentials.

---

## Troubleshooting

### Docker Compose Builds Even Without `--build`

If a service has a `build:` section and the image does not exist yet, Docker Compose may build it automatically.

To avoid building, use an existing image or run:

```bash
docker compose up -d --no-build
```

### n8n Cannot Find Output Files

Check that the project output folder is mounted into the n8n container and that the internal path exists:

```bash
docker exec -it <n8n-container-name> ls -lah /home/node/.n8n-files
```

### Ollama Does Not Respond

Confirm Ollama is running:

```bash
ollama list
```

If running through Docker, confirm the container is up:

```bash
docker ps
```

### API Does Not Start

Check dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## Roadmap

Possible extensions:

- Streamlit dashboard for browsing collected papers
- PDF download and ingestion
- Local vector database
- RAG assistant for paper Q&A
- Zotero synchronization
- Topic trend visualization
- Author and journal analytics
- Manual relevance feedback for better ranking

---


## License


This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.

---

## Citation / Attribution

If this project helps your research workflow, consider citing or linking to the repository in related documentation, talks, or project pages.

## Disclaimer

This project provides AI-assisted literature collection and summarization for research support purposes only.

Generated summaries may contain inaccuracies or incomplete interpretations. Always verify scientific claims, numerical values, and conclusions directly from the original publications.

## Contributing

Contributions, suggestions, and workflow improvements are welcome.

Possible contribution areas include:
- additional literature sources
- improved ranking logic
- RAG integration
- dashboard extensions
- citation manager integrations
- visualization tools
