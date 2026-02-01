# Deployment Guide for Pleader AI

This project is ready for production-level deployment. Because it uses a separate Backend (FastAPI) and Frontend (React), we recommend deploying them to specialized services for the best performance and stability.

**Recommended Stack:**
*   **Database:** Supabase (Already configured)
*   **Backend:** Render (Web Service)
*   **Frontend:** Vercel (Static Site Hosting)

---

## 1. Prerequisites

Ensure you have your **Supabase** credentials and **Google Gemini API Key** ready. You will need:
*   `SUPABASE_URL`
*   `SUPABASE_KEY`
*   `GEMINI_API_KEY`
*   `JWT_SECRET` (You can generate a random string for this)

---

## 2. Deploy Backend (Render)

Render is excellent for Python applications.

1.  Create an account at [render.com](https://render.com).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository: `ashokkumarboya93/pleader.io`
4.  **Configure the service:**
    *   **Name:** `pleader-backend` (or similar)
    *   **Region:** Choose one close to you (e.g., Singapore or Frankfurt for India/Europe)
    *   **Branch:** `main`
    *   **Root Directory:** `.` (Leave empty or set to root)
    *   **Environment:** `Python 3`
    *   **Build Command:** `pip install -r backend/requirements.txt`
    *   **Start Command:** `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
        *   *Note:* Using the `Procfile` I created, Render might auto-detect this. If not, use the command above.
5.  **Environment Variables:**
    Scroll down to "Environment Variables" and add:
    *   `SUPABASE_URL`: (Your verified Supabase URL)
    *   `SUPABASE_KEY`: (Your Service Role Key or Anon Key)
    *   `GEMINI_API_KEY`: (Your Google Gemini API Key)
    *   `JWT_SECRET`: (A long random string)
    *   `PYTHON_VERSION`: `3.10.0` (Recommended)
6.  **Deploy:** Click "Create Web Service".

> **Important Note on RAG (Document Search):**
> The current RAG implementation uses a **local file-based index**. On the free tier of Render, the filesystem is *ephemeral*, meaning it resets every time the server restarts.
> *   **Consequence:** Documents uploaded via the app will be saved to Supabase (metadata), but the "search index" will be lost on restart until you upload them again or we implement a re-indexing feature.
> *   **Fix:** For true production persistence of the search index, upgrade to a Render plan with **Persistent Disk** and mount it to `/app/backend/faiss_index`.

---

## 3. Deploy Frontend (Vercel)

Vercel is the creators of standard React deployment workflows.

1.  Create an account at [vercel.com](https://vercel.com).
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository: `ashokkumarboya93/pleader.io`
4.  **Configure Project:**
    *   **Framework Preset:** Create React App (should auto-detect)
    *   **Root Directory:** Click "Edit" and select `frontend`. **This is crucial.**
5.  **Environment Variables:**
    You need to tell the frontend where the Backend is living.
    *   `REACT_APP_API_URL`: `https://<YOUR-RENDER-BACKEND-URL>.onrender.com/api`
    *   (Make sure to remove the trailing slash if your code appends one, or add `/api` if your code expects base URL only. Check `src/lib/api.js` or similar if unsure. Based on standard setups, providing the full API base is safest).
6.  **Deploy:** Click "Deploy".

---

## 4. Final Configuration

Once both are deployed:
1.  **Frontend -> Backend Connection:** Ensure `REACT_APP_API_URL` in Vercel points to your active Render URL.
2.  **CORS (Backend):**
    *   Currently, the backend allows ALL origins (`[*]`). This is easy for setup but less secure for strict production.
    *   To tighten security, update `server.py` to only allow your Vercel domain in `allow_origins`.

## 5. Summary
*   **Code:** Pushed to GitHub.
*   **Backend:** Running on Render (Python/FastAPI).
*   **Frontend:** Running on Vercel (React).
*   **Database:** Hosted on Supabase.

Your application is now "Production Ready"!