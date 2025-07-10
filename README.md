# Andrea Payroll Audit

## How to Run

Prepare .env file with the following variables:

```bash
OPENAI_API_KEY=
REDIS_URI = "redis://localhost:6379/0" # Redis URI
MODEL_NAME=o4-mini # Reasoning model
REASONING_EFFORTS="high"  # (or None if you are using a non-reasoning model like gpt-4.1, gpt-4o and the mini ones.)
```

```bash
uv venv # make sure to have uv installed, check (https://docs.astral.sh/uv/getting-started/installation/)
source .venv/bin/activate
uv sync

sh run.sh
```
Open http://localhost:8503/ to access the UI.

## Monitoring Logs

You can monitor service and UI logs using the following commands:

```bash
# Monitor service logs
tail -f logs/service.log

# Monitor UI logs
tail -f logs/ui.log
```

Note:
- When you upload the file, it autocreates a directory locally called `data` and stores the files there with a uuid name for each session.

## UI Usage

- The UI is a Streamlit app that allows you to upload files and run the audit.
- Upload files and click on "Lock & Load Files" to save them.
- Write your tasks in the text area and click on "LAUNCH AI AUDIT" to run the audit.
- Click on "LAUNCH AI AUDIT" to run the audit.
- Wait for the audit to finish.
- The results will be displayed in the UI.
- You can Export the results as a JSON file.
- Give the UI like 5-10 seconsds to render :D 