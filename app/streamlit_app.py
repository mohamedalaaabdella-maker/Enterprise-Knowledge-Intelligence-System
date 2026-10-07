"""
Enterprise Knowledge Intelligence System - Gradio UI

Only the interface lives here. All retrieval, reranking, query rewriting,
relevance checking and generation logic stays in src.pipeline.RAGServices.
"""

import html
import logging

import gradio as gr

from src.pipeline import RAGServices


logger = logging.getLogger(__name__)


# =========================================================
# Configuration (unchanged backend parameters)
# =========================================================

RETRIEVAL_K = 20
RERANK_K = 5
MAX_REWRITES = 1

TITLE = "Enterprise Knowledge Intelligence System"
SUBTITLE = "AI-powered technical documentation assistant"
DESCRIPTION = (
    "Ask questions about Python, FastAPI, Docker, PostgreSQL, and Git "
    "using a hybrid RAG pipeline."
)
BADGES = ["Python", "FastAPI", "Docker", "PostgreSQL", "Git", "RAG"]

EXAMPLE_QUESTIONS = [
    "How does dependency injection work in FastAPI?",
    "How do I create a Docker volume?",
    "How do I create an index in PostgreSQL?",
    "How do I undo the last Git commit?",
]


# =========================================================
# Load RAG System (once, at startup)
# =========================================================

print("Loading RAG system...")

rag = RAGServices()

print("RAG system loaded successfully.")


# =========================================================
# Formatting Helpers (HTML / Markdown only, no RAG logic)
# =========================================================

def esc(value) -> str:
    """Escape any value for safe HTML display."""
    return html.escape(str(value))


def render_header() -> str:
    badges = "".join(f'<span class="badge">{esc(b)}</span>' for b in BADGES)
    return f"""
<div class="app-header">
    <h1>{esc(TITLE)}</h1>
    <h2>{esc(SUBTITLE)}</h2>
    <p>{esc(DESCRIPTION)}</p>
    <div class="badges">{badges}</div>
</div>
"""


def render_system_status() -> str:
    items = [
        ("Retrieval", "Hybrid"),
        ("Reranking", f"Top {RERANK_K}"),
        ("Query Rewriting", "Enabled"),
        ("Relevance Check", "Enabled"),
        ("Generation", "LLM"),
    ]
    cells = "".join(
        f"""
        <div class="status-item">
            <span class="status-dot"></span>
            <div>
                <div class="status-label">{esc(label)}</div>
                <div class="status-value">{esc(value)}</div>
            </div>
        </div>
        """
        for label, value in items
    )
    return f'<div class="status-grid">{cells}</div>'


def render_empty_state() -> str:
    return """
<div class="state-card">
    <div class="state-title">Ask a question to search the enterprise knowledge base.</div>
    <div class="state-text">
        Answers are generated from retrieved documentation, and the
        supporting sources are listed below each answer.
    </div>
</div>
"""


def render_loading_state() -> str:
    return """
<div class="state-card loading">
    <div class="state-title"><span class="spinner"></span>Processing your question...</div>
    <div class="state-text">
        Running hybrid retrieval, reranking, relevance check, and answer generation.
        This may take a few moments.
    </div>
</div>
"""


def render_message_state(title: str, text: str, kind: str = "warning") -> str:
    return f"""
<div class="state-card {esc(kind)}">
    <div class="state-title">{esc(title)}</div>
    <div class="state-text">{esc(text)}</div>
</div>
"""


def render_retrieval_info(question, result) -> str:
    query_used = result.get("query_used", question)
    rewritten = bool(result.get("rewritten", False))
    rewrite_count = result.get("rewrite_count", 0)
    relevant = bool(result.get("relevant", False))
    documents = result.get("documents") or []

    rows = [
        ("Original Query", question),
        ("Query Used", query_used),
        ("Query Rewritten", "Yes" if rewritten else "No"),
        ("Rewrite Count", rewrite_count),
        (
            "Relevance Check",
            "Relevant context found" if relevant else "No relevant context found",
        ),
        ("Number of Sources", len(documents)),
    ]

    body = "".join(
        f"<tr><th>{esc(label)}</th><td>{esc(value)}</td></tr>"
        for label, value in rows
    )
    return f'<table class="info-table">{body}</table>'


def render_sources(documents) -> str:
    if not documents:
        return render_message_state(
            "No sources retrieved",
            "The retrieval step did not return any documents for this question.",
            kind="warning",
        )

    cards = []

    for index, document in enumerate(documents, start=1):
        metadata = document.metadata or {}

        document_id = metadata.get("document_id", "Unknown document")
        domain = metadata.get("domain", "Unknown domain")
        chunk_id = metadata.get("chunk_id", "Unknown chunk")
        section = (
            metadata.get("Header 1")
            or metadata.get("Header 2")
            or metadata.get("Header 3")
            or "Unknown section"
        )
        content = (document.page_content or "").strip()

        cards.append(f"""
<div class="source-card">
    <div class="source-title">Source #{index}</div>
    <div class="source-meta">
        <div><span>Document</span><code>{esc(document_id)}</code></div>
        <div><span>Domain</span><code>{esc(domain)}</code></div>
        <div><span>Section</span><code>{esc(section)}</code></div>
        <div><span>Chunk</span><code>{esc(chunk_id)}</code></div>
    </div>
    <details>
        <summary>View retrieved content</summary>
        <pre class="source-content">{esc(content)}</pre>
    </details>
</div>
""")

    return "".join(cards)


# =========================================================
# Event Handlers
# =========================================================

def answer_question(question):
    """
    Run the RAG pipeline and update the UI.

    This is a generator: the first yield shows the loading state,
    the second yield shows the final result (or a friendly error).
    """

    hide = gr.update(visible=False)

    if not question or not question.strip():
        yield (
            gr.update(
                value=render_message_state(
                    "Please enter a question",
                    "Type a technical question above and press Ask Question.",
                ),
                visible=True,
            ),
            hide, hide, hide, hide, hide,
        )
        return

    question = question.strip()

    # ----- Loading state -----
    yield (
        gr.update(value=render_loading_state(), visible=True),
        hide, hide, hide, hide, hide,
    )

    try:
        result = rag.ask(
            question=question,
            retrieval_k=RETRIEVAL_K,
            rerank_k=RERANK_K,
            max_rewrites=MAX_REWRITES,
        )

        answer = result["answer"]
        documents = result.get("documents") or []

        # ----- Result state -----
        yield (
            gr.update(visible=False),
            gr.update(value=answer, visible=True),
            gr.update(visible=True),
            gr.update(value=render_retrieval_info(question, result)),
            gr.update(visible=True),
            gr.update(value=render_sources(documents)),
        )

    except Exception:
        # Full details go to the console only
        logger.exception("RAG pipeline failed")

        yield (
            gr.update(
                value=render_message_state(
                    "Something went wrong",
                    "The system could not process your question. "
                    "Please try again or rephrase it.",
                    kind="error",
                ),
                visible=True,
            ),
            hide, hide, hide, hide, hide,
        )


def clear_all():
    hide = gr.update(visible=False)
    return (
        "",                                              # question
        gr.update(value=render_empty_state(), visible=True),
        hide, hide, hide, hide,                          # answer + accordions
    )


# =========================================================
# Styling
# =========================================================

CSS = """
:root, .dark {
    --bg: #0b1220;
    --card: #111a2e;
    --card-alt: #0e1627;
    --border: #1f2c47;
    --text: #e6edf7;
    --muted: #8fa1bd;
    --accent: #38bdf8;
    --accent-strong: #2563eb;
    --ok: #34d399;
    --err: #f87171;
    --warn: #fbbf24;
}

body, .gradio-container {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.gradio-container {
    max-width: 1000px !important;
    margin: 0 auto !important;
    padding: 24px 16px !important;
}

footer { display: none !important; }

/* Header */
.app-header { padding: 8px 0 20px 0; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
.app-header h1 { font-size: 1.9rem; font-weight: 700; margin: 0 0 4px 0; color: var(--text); }
.app-header h2 { font-size: 1.05rem; font-weight: 500; margin: 0 0 10px 0; color: var(--accent); }
.app-header p { margin: 0 0 14px 0; color: var(--muted); }
.badges { display: flex; flex-wrap: wrap; gap: 8px; }
.badge {
    font-size: 0.78rem; padding: 3px 10px; border-radius: 999px;
    border: 1px solid var(--border); background: var(--card); color: var(--muted);
}

/* Section titles */
.section-title { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--muted); margin: 22px 0 8px 0; font-weight: 600; }

/* Question input */
.question-box textarea {
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 10px !important;
    font-size: 1rem !important; padding: 14px !important;
}
.question-box textarea:focus { border-color: var(--accent) !important; }

button.primary-btn {
    background: var(--accent-strong) !important; border: none !important;
    color: #fff !important; font-weight: 600 !important; border-radius: 8px !important;
}
button.primary-btn:hover { filter: brightness(1.1); }
button.secondary-btn {
    background: transparent !important; border: 1px solid var(--border) !important;
    color: var(--muted) !important; border-radius: 8px !important;
}

/* Answer card */
.answer-card {
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-left: 3px solid var(--accent) !important; border-radius: 10px !important;
    padding: 20px 24px !important; font-size: 1.02rem; line-height: 1.65;
}
.answer-card code, .answer-card pre { background: var(--card-alt) !important; }

/* State cards (empty / loading / error) */
.state-card {
    background: var(--card); border: 1px dashed var(--border); border-radius: 10px;
    padding: 28px 24px; text-align: center;
}
.state-card.loading { border-style: solid; border-color: var(--accent); }
.state-card.error { border-style: solid; border-color: var(--err); }
.state-card.warning { border-style: solid; border-color: var(--warn); }
.state-title { font-weight: 600; color: var(--text); margin-bottom: 6px; }
.state-text { color: var(--muted); font-size: 0.92rem; }
.spinner {
    display: inline-block; width: 14px; height: 14px; margin-right: 10px;
    border: 2px solid var(--border); border-top-color: var(--accent);
    border-radius: 50%; vertical-align: -2px; animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* System status */
.status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.status-item {
    display: flex; align-items: center; gap: 10px; padding: 10px 12px;
    background: var(--card); border: 1px solid var(--border); border-radius: 8px;
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--ok); flex: none; }
.status-label { font-size: 0.72rem; color: var(--muted); }
.status-value { font-size: 0.9rem; font-weight: 600; color: var(--text); }

/* Accordions */
.gradio-container .block.accordion, .gradio-container .accordion {
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Retrieval table */
.info-table { width: 100%; border-collapse: collapse; }
.info-table th, .info-table td {
    text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--border);
    font-size: 0.92rem; vertical-align: top;
}
.info-table th { width: 200px; color: var(--muted); font-weight: 500; }
.info-table td { color: var(--text); word-break: break-word; }

/* Sources */
.source-card {
    background: var(--card-alt); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px; margin-bottom: 12px;
}
.source-title { font-weight: 600; color: var(--accent); margin-bottom: 10px; }
.source-meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px 16px; }
.source-meta span { display: block; font-size: 0.72rem; color: var(--muted); margin-bottom: 2px; }
.source-meta code {
    background: var(--card); border: 1px solid var(--border); border-radius: 4px;
    padding: 2px 6px; font-size: 0.85rem; color: var(--text); word-break: break-all;
}
.source-card details { margin-top: 12px; }
.source-card summary { cursor: pointer; color: var(--muted); font-size: 0.88rem; }
.source-card summary:hover { color: var(--accent); }
.source-content {
    margin: 10px 0 0 0; padding: 12px; background: var(--card);
    border: 1px solid var(--border); border-radius: 8px; color: var(--text);
    white-space: pre-wrap; word-break: break-word; font-size: 0.85rem;
    max-height: 320px; overflow-y: auto;
}

@media (max-width: 700px) {
    .app-header h1 { font-size: 1.45rem; }
    .info-table th { width: 120px; }
}
"""

FORCE_DARK_JS = """
() => {
    document.body.classList.add('dark');
}
"""

THEME = gr.themes.Base(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
)


# =========================================================
# Gradio UI
# =========================================================

def build_ui() -> gr.Blocks:

    with gr.Blocks(
        title=TITLE,
        theme=THEME,
        css=CSS,
        js=FORCE_DARK_JS,
    ) as demo:

        # ----- Header -----
        gr.HTML(render_header())

        # ----- System status -----
        gr.HTML('<div class="section-title">System Status</div>')
        gr.HTML(render_system_status())

        # ----- Question -----
        gr.HTML('<div class="section-title">Ask a Question</div>')

        question_input = gr.Textbox(
            label="Your Question",
            show_label=False,
            placeholder="Ask a technical question about the documentation...",
            lines=3,
            elem_classes="question-box",
        )

        with gr.Row():
            ask_button = gr.Button(
                "Ask Question",
                variant="primary",
                scale=3,
                elem_classes="primary-btn",
            )
            clear_button = gr.Button(
                "Clear",
                variant="secondary",
                scale=1,
                elem_classes="secondary-btn",
            )

        gr.Examples(
            examples=[[q] for q in EXAMPLE_QUESTIONS],
            inputs=question_input,
            label="Example questions",
        )

        # ----- Answer -----
        gr.HTML('<div class="section-title">Answer</div>')

        state_output = gr.HTML(value=render_empty_state())

        answer_output = gr.Markdown(
            visible=False,
            elem_classes="answer-card",
        )

        # ----- Retrieval information -----
        with gr.Accordion(
            "Retrieval Information",
            open=False,
            visible=False,
        ) as retrieval_accordion:
            retrieval_output = gr.HTML()

        # ----- Sources -----
        with gr.Accordion(
            "Retrieved Sources",
            open=False,
            visible=False,
        ) as sources_accordion:
            sources_output = gr.HTML()

        # ----- Events -----
        outputs = [
            state_output,
            answer_output,
            retrieval_accordion,
            retrieval_output,
            sources_accordion,
            sources_output,
        ]

        ask_button.click(
            fn=answer_question,
            inputs=question_input,
            outputs=outputs,
        )

        question_input.submit(
            fn=answer_question,
            inputs=question_input,
            outputs=outputs,
        )

        clear_button.click(
            fn=clear_all,
            inputs=None,
            outputs=[question_input] + outputs[:1] + [
                answer_output,
                retrieval_accordion,
                retrieval_output,
                sources_accordion,
            ],
        )

    return demo


demo = build_ui()


# =========================================================
# Launch
# =========================================================

if __name__ == "__main__":
    demo.queue()
    demo.launch(share=True)