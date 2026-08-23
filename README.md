# Pneumonia Assistant Platform

## Overall Project Explanation

This project is an end to end AI assisted pneumonia platform with three major capabilities:

1. Chest X ray prediction API for pneumonia classification.
2. Guideline aware question answering using a Retrieval Augmented Generation pipeline over a WHO clinical PDF.
3. Multi client access through a web frontend and a mobile app codebase.

At a high level, users authenticate with JWT, upload chest X ray images for prediction, and ask medical guideline questions through a RAG endpoint that retrieves evidence from the local PDF and returns an answer with citations.

The backend is built with Django and Django REST Framework, the web client is built with React plus Vite, and the repository also contains React Native mobile app source files.

## Key Features

- JWT authentication and token refresh
- User registration endpoint
- Protected pneumonia prediction endpoint
- RAG query endpoint with idempotency support
- Citation aware RAG responses from the pneumonia guideline PDF
- OCR first ingestion path for scanned or mixed quality PDF content

## Repository Structure

- backend/project
	- Django backend project
	- API app with auth, prediction, and RAG endpoints
	- Services for CNN inference and RAG response generation
	- ML modules for CNN architecture and PDF retrieval logic
	- Local model artifact model.pth and guideline PDF pneumonia_pdf.pdf
- pneumonia_frontend
	- React plus Vite web application
	- Login, registration, protected routes, prediction, and RAG UI pages
- mob
	- React Native app source files and screens
- model
	- Experimental notebooks for model exploration

## High Level Architecture

1. Client sends request to Django API.
2. Authenticated users can upload image files for pneumonia prediction.
3. RAG requests are processed by hybrid retrieval over the PDF.
4. Backend returns response JSON to web or mobile clients.

For RAG requests:

1. PDF pages are OCR processed when needed and cached.
2. Text is chunked and indexed.
3. Hybrid retrieval combines dense style ranking and keyword ranking with fallback support.
4. Answer text is composed from top relevant evidence snippets.
5. Citations include page and section metadata.

## Technology Stack

- Backend: Django, Django REST Framework, SimpleJWT
- ML and retrieval: PyTorch, FAISS, sentence-transformers, scikit-learn
- OCR and PDF utilities: Tesseract OCR and Ghostscript
- Web frontend: React, Vite, Tailwind
- Mobile: React Native source structure

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- npm
- Tesseract OCR installed on system
- Ghostscript installed on system

On macOS with Homebrew:

```bash
brew install tesseract ghostscript
```

## Backend Setup

From repository root:

```bash
cd backend/project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend default URL:

- http://127.0.0.1:8000

## Web Frontend Setup

From repository root:

```bash
cd pneumonia_frontend
npm install
npm run dev
```

By default, frontend API base URL points to:

- http://127.0.0.1:8000

You can override with environment variable VITE_API_BASE_URL.

## Mobile App Notes

The repository includes mobile source files under the mob folder. If you plan to run this app directly, add or align the React Native or Expo project configuration and package scripts for your target workflow.

## Main API Endpoints

Base path:

- /api

Endpoints:

- POST /api/user/create
	- Create user with username and password
- POST /api/token/
	- Obtain JWT access and refresh tokens
- POST /api/token/refresh/
	- Refresh JWT token
- POST /api/predict/
	- Auth required
	- Multipart form with file field
- GET /api/rag-query/?query=...
	- Requires Idempotency-Key header
	- Returns answer, citations, cached fields

## Example RAG Request

```bash
curl -X GET "http://127.0.0.1:8000/api/rag-query/?query=What%20is%20recommended%20for%20chest-indrawing%20pneumonia%3F" \
	-H "Idempotency-Key: demo-key-001"
```

## Example Predict Request

```bash
curl -X POST "http://127.0.0.1:8000/api/predict/" \
	-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
	-F "file=@/path/to/xray.jpg"
```

## Notes and Operational Guidance

- First RAG query can be slower because OCR and chunk index preparation may run.
- OCR cache is stored locally to speed up later queries.
- If dense embedding model is not available locally, the retrieval system uses a local fallback path to remain functional.
- This project is for educational and engineering purposes, not a replacement for clinical diagnosis by qualified professionals.

## Future Improvements

- Add full reranker model for stronger citation ranking quality
- Add structured table extraction for guideline tables
- Add automated tests for RAG and prediction endpoints
- Add production deployment profiles and environment based settings
