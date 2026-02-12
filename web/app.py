import json
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.analysis import technical_analysis, fundamental_analysis, piotroski_fscore, canslim_analysis
from core.tickers import search_tickers

app = FastAPI(title="Stock Analyzer")

TEMPLATE_DIR = Path(__file__).parent / "templates"


@app.get("/", response_class=HTMLResponse)
async def index():
    return (TEMPLATE_DIR / "index.html").read_text()


@app.get("/api/search")
async def search(q: str = ""):
    return search_tickers(q)


@app.get("/api/analyze/{symbol}")
async def analyze(symbol: str):
    symbol = symbol.strip().upper()

    async def event_stream():
        # Stream technical analysis sections
        try:
            for section in technical_analysis(symbol):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "technical",
                        **section,
                    }),
                }
        except ValueError as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }
            return

        # Stream fundamental analysis sections
        try:
            for section in fundamental_analysis(symbol):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "fundamental",
                        **section,
                    }),
                }
        except ValueError as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }
            return

        # Stream Piotroski F-Score sections
        try:
            for section in piotroski_fscore(symbol):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "piotroski",
                        **section,
                    }),
                }
        except ValueError as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }
            return

        # Stream CAN SLIM analysis sections
        try:
            for section in canslim_analysis(symbol):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "canslim",
                        **section,
                    }),
                }
        except ValueError as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }
            return

        yield {
            "event": "done",
            "data": json.dumps({"status": "complete"}),
        }

    return EventSourceResponse(event_stream())
