from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from src.chat.engine import ChatEngine
from src.config import KNOWLEDGE_DIR, SUPPORTED_EXTENSIONS
from src.knowledge.store import KnowledgeStore

store = KnowledgeStore()
engine = ChatEngine(store)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    app.secret_key = "rei-cai-demo"

    @app.get("/")
    def home():
        sources = store.list_sources()
        return render_template(
            "home.html",
            file_count=len(sources),
            chunk_count=len(store.documents),
        )

    @app.route("/admin", methods=["GET", "POST"])
    def admin():
        if request.method == "POST":
            action = request.form.get("action")

            if action == "upload":
                files = request.files.getlist("files")
                uploaded = 0
                for file in files:
                    if not file or not file.filename:
                        continue
                    filename = secure_filename(file.filename)
                    if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
                        continue
                    file.save(KNOWLEDGE_DIR / filename)
                    uploaded += 1
                flash(f"已上传 {uploaded} 个文件")

            elif action == "rebuild":
                count = store.rebuild()
                flash(f"索引完成，共 {count} 个知识片段")

            elif action == "delete":
                filename = request.form.get("filename", "")
                if filename:
                    store.delete_source(filename)
                    flash(f"已删除 {filename}")

            return redirect(url_for("admin"))

        return render_template("admin.html", sources=store.list_sources())

    @app.get("/chat")
    def chat():
        return render_template("chat.html")

    @app.post("/api/chat")
    def api_chat():
        data = request.get_json(silent=True) or {}
        question = (data.get("question") or "").strip()
        if not question:
            return jsonify({"error": "问题不能为空"}), 400

        answer, hits = engine.answer(question)
        sources = sorted({hit["source"] for hit in hits})
        return jsonify({"answer": answer, "sources": sources})

    return app
