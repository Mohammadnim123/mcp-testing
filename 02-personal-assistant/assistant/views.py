import json
import os
import tempfile

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .agent import run_agent
from .ingest import ingest_data


def chat_view(request):
    """Render the chat UI."""
    return render(request, 'assistant/chat.html')


@csrf_exempt
@require_http_methods(["POST"])
async def api_chat(request):
    """Handle chat API requests."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    message = body.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "message is required"}, status=400)

    session_id = body.get("sessionId", "default")
    mode = body.get("mode", "rag")

    try:
        result = await run_agent(message, session_id, mode)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
async def api_ingest(request):
    """Handle PDF file upload and ingestion."""
    if not request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    uploaded_file = request.FILES.get("file")
    if uploaded_file is None:
        return JsonResponse({"error": "No file field in upload"}, status=400)

    if not uploaded_file.name.lower().endswith(".pdf"):
        return JsonResponse({"error": "Only PDF files are accepted"}, status=400)

    if uploaded_file.size > 25 * 1024 * 1024:
        return JsonResponse({"error": "File exceeds 25MB limit"}, status=400)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        await ingest_data(tmp_path)
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
