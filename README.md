# Andrea Payroll Audit

## How to Run

```bash
uv venv
source .venv/bin/activate
uv sync

sh run.sh
```

## Monitoring Logs

You can monitor service and UI logs using the following commands:

```bash
# Monitor service logs
tail -f logs/service.log

# Monitor UI logs
tail -f logs/ui.log
```