# HAGAI AI CLOUD

HAGAI AI CLOUD ni mwanzo wa jukwaa la Hybrid AI: dashboard ya wavuti, FastAPI backend, na Ollama kama model runtime.

## Muundo
- `docs/index.html`: dashboard ya wavuti (inaweza kuchapishwa kwa GitHub Pages).
- `backend/main.py`: API iliyolindwa kwa API key.
- `backend/Dockerfile`: image ya backend.
- `backend/requirements.txt`: dependencies.

## Muhimu kuhusu gharama na uwezo
Programu hizi ni open-source, lakini hosting, GPU, umeme, storage na intaneti si bure bila kikomo. GitHub Pages inahost dashboard tuli tu; haiendeshi FastAPI au Ollama. Kwa matumizi ya AI ya 24/7, backend na Ollama lazima viwe kwenye mashine/seva inayowashwa na kuunganishwa na intaneti. Kompyuta ikizimwa, AI haitapatikana.

## Kuendesha kwenye kompyuta ya Windows (njia rahisi)
1. Pakua repository kama ZIP kupitia GitHub: Code → Download ZIP, kisha fungua ZIP.
2. Sakinisha Python 3.11+ na Ollama.
3. Fungua folda `backend` na bofya mara mbili `start_windows.bat`. Script itaweka dependencies, itatengeneza API key ya session na kufungua dashboard kwenye `http://127.0.0.1:8000`.
4. Weka API key iliyoonyeshwa kwenye sehemu API & Muunganisho ya dashboard. Acha dirisha la terminal wazi wakati unatumia AI.

## Njia ya kuanzisha kwa mkono
1. Sakinisha Python 3.11+ na Ollama.
2. Pakua modeli ndogo inayolingana na RAM yako, kwa mfano `ollama pull llama3.2:1b` (inahitaji nafasi ya diski na RAM; usijaribu kama kifaa hakina nafasi).
3. Ingia kwenye folda `backend`, tengeneza virtual environment na sakinisha dependencies:
   `python -m venv .venv`
   Windows: `.venv\\Scripts\\activate`
   Linux/macOS: `source .venv/bin/activate`
   `pip install -r requirements.txt`
4. Weka environment variable `HAGAI_API_KEY` yenye siri ndefu. Usiiweke kwenye GitHub wala kuituma kwa mtu.
5. Hakikisha Ollama inafanya kazi, kisha anzisha API:
   `uvicorn main:app --host 127.0.0.1 --port 8000`
6. Fungua `http://127.0.0.1:8000/docs` kuthibitisha API.
7. Fungua dashboard ya GitHub Pages au `docs/index.html`, kisha kwenye API & Muunganisho weka Backend URL na API key.

## Endpoints
- `GET /api/health` — health check (haifichui siri).
- `GET /api/models` — modeli zilizopo (Bearer API key).
- `POST /api/chat` — mazungumzo na modeli (Bearer API key).
- `POST /api/models/pull` — pakua modeli kupitia Ollama (Bearer API key).
- `GET/POST /api/datasets` — orodha/pakia TXT, CSV, JSONL hadi 10MB (Bearer API key).

## Usalama
- Usifungue bandari ya Ollama 11434 moja kwa moja kwenye intaneti.
- Tumia HTTPS, API key ndefu na CORS yenye domain ya dashboard pekee kwenye deployment.
- API key inayowekwa kwenye browser ni ya mtumiaji mmoja/admin; si mfumo wa multi-user authentication.
- Kwa deployment ya cloud, Ollama lazima ipatikane kwa backend kupitia private network au tunnel salama. Usitumie `127.0.0.1` ya cloud container kutarajia kufikia kompyuta yako.

## Kile ambacho bado hakijajengwa
Fine-tuning/training halisi, multi-user accounts, billing/quotas, GPU scheduler, automatic backups na high-availability. Hivi vinahitaji miundombinu ya ziada; dashboard haitadai vimefanyika kabla havijatekelezwa.
