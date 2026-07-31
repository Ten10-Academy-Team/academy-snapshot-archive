# Academy Snapshot Archive

A searchable, filterable archive of all Academy Snapshot newsletter issues.

**Live page:** https://ten10-academy-team.github.io/academy-snapshot-archive/  
**Embed page (for Google Sites):** https://ten10-academy-team.github.io/academy-snapshot-archive/embed.html

---

## Adding a New Issue

### Quick Steps

1. **Drop the file(s)** into a new folder: `Issue XX/` (or `Issue XX - Edition Name/`)
2. **Run the script:**
   ```
   python add_issue.py
   ```
3. **Follow the prompts** — the script will:
   - Read the PDF/PNG and show you the extracted text
   - Ask you to confirm the person's details
   - Update `snapshot_data.json`
   - Rebuild `embed.html` with the new data
   - Commit and push to GitHub

The page updates automatically within ~1 minute of pushing.

### Manual Steps (if you prefer)

1. Add the file to `Issue XX/` folder
2. Add an entry to `snapshot_data.json`:
   ```json
   {
     "issue": 61,
     "date": "July 2026",
     "name": "First Last",
     "academy": 40,
     "client": "Client Name",
     "role": "Job Title",
     "roleCategory": "Test",
     "specialism": "Automation",
     "tools": ["Jira", "Selenium"],
     "methodology": "Agile",
     "location": "Hybrid (2 days office)",
     "relocated": false,
     "sector": "Banking/Financial",
     "editionType": "Standard",
     "fileFormat": "pdf",
     "sourceFiles": ["Issue 61/filename.pdf"]
   }
   ```
3. Run `python rebuild_embed.py` to update the embed page
4. `git add . && git commit -m "Add Issue 61" && git push`

---

## Field Reference

| Field | Values |
|-------|--------|
| roleCategory | Test, Dev, BA, PM, DevOps, Security, Data, Service Desk, Internal |
| specialism | Automation, Manual / Functional, Performance, Accessibility, Aviation Systems, Data, Cloud / Architecture, Cyber Security, etc. |
| editionType | Standard, Christmas Edition, Easter Edition, Halloween Edition, Ten10 Award Winners Edition, Talent Team Edition, International Women's Day Edition, Bench Edition |
| fileFormat | pdf, png, jpg |

---

## Project Structure

```
snapshot/
├── index.html          # Full archive page (standalone)
├── embed.html          # Lightweight page for Google Sites embed
├── viewer.html         # Document viewer (renders PDFs/images cleanly)
├── snapshot_data.json  # All entry data
├── add_issue.py        # Script to add new issues
├── robots.txt          # Blocks search engines
├── Issue 1/            # Source files per issue
├── Issue 2/
├── ...
└── Issue 60/
```

## Requirements

- Python 3.x
- `pymupdf` (for PDF text extraction): `pip install pymupdf`
- Git + GitHub CLI (`gh`) for pushing
