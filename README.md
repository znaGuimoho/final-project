# Final Project - House Renting Website

A full-stack house renting platform built with **FastAPI** (Python) and **PostgreSQL**. Users can register, log in, browse available houses, and hosts can list their properties with images and detailed information.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-supported-blue)

## 🚀 Features

- User registration & login (session-based authentication)
- Home page with dynamic house listings loaded from database
- Host dashboard – upload house photos (stored locally) and details
- About Us, Renting Tips, My Favorites, Contact Us pages
- FAQs, Terms & Conditions
- Fully containerized with Docker

## 🛠 Tech Stack

| Layer             | Technology                          |
|-------------------|-------------------------------------|
| Backend           | FastAPI (Python)                    |
| Database          | PostgreSQL                          |
| Authentication    | Session-based                       |
| File Storage      | Local filesystem (uploaded images)  |
| Deployment        | Docker + Docker Compose             |

## 📦 Project Structure

finalProject/
├── backend/                  # FastAPI backend
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Environment variables (gitignored)
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # App configuration
│   │   ├── cert.pem          # SSL certificate (for HTTPS)
│   │   ├── key.pem           # SSL private key
│   │   ├── routers/          # API routes
│   │   │   ├── auth.py       # Login / Register / Session handling
│   │   │   ├── home.py       # Home page listings endpoint
│   │   │   ├── hoster.py     # Host property upload & management
│   │   │   └── more.py       # About, FAQs, Contact, etc.
│   │   ├── services/
│   │   │   ├── Hash_password.py
│   │   │   └── user_service.py
│   │   └── static/
│   │       └── uploads/      # User-uploaded house images (local storage)
│   └── imgs.png              # Example/placeholder image
│
├── frontend/                 # Static frontend (served by FastAPI)
│   ├── css/
│   │   ├── aboutUs.css
│   │   ├── base.css
│   │   ├── home.css
│   │   ├── host.css
│   │   ├── login.css
│   │   ├── register.css
│   │   ├── retalTips.css          # ← note: typo in original (rentalTips)
│   │   ├── termsAndConditions.css
│   │   └── uploadSucsess.css      # ← typo: uploadSuccess.css
│   │
│   ├── imgs/
│   │   ├── house.png
│   │   ├── logo-home-png-7429.png
│   │   ├── Me.png
│   │   └── photo-for-more.jpeg
│   │
│   ├── scripts/              # JavaScript files
│   │   ├── home.js
│   │   ├── login.js
│   │   ├── register.js
│   │   ├── host.js
│   │   ├── aboutUs.js
│   │   ├── rentalTips.js
│   │   ├── terms.js
│   │   └── uploadSuccess.js
│   │
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── host.html
│   ├── aboutUs.html
│   ├── rentalTips.html
│   ├── terms.html
│   └── uploadSuccess.html
│
├── .gitignore
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Backend container build
└── README.md

## 🚀 Setup & Running the Project

### Prerequisites
Make sure you have these installed:
- [Docker & Docker Compose](https://www.docker.com/get-started) (Recommended & easiest way)
- OR Python 3.11+ and PostgreSQL (if you prefer running without Docker)

### Method 1: Run with Docker (Recommended – One command!)

1. **Clone the repository**
   ```bash
   $ git clone https://github.com/znaGuimoho/finalProject.git
   $ cd finalProject

2. **Create your environment file**
    $ cp backend/.env.example backend/.env

    Then edit backend/.env and fill in your PostgreSQL credentials (or leave defaults if using Docker's DB):

    $ DATABASE_URL=postgresql://postgres:password@db:5432/house_renting
    $ SECRET_KEY=your-super-secret-jwt-key-here

3. **Start everything (FastAPI + PostgreSQL)**

    $ docker-compose up --build

4. **Open the app**

Visit: https://localhost:8000 (HTTPS with your self-signed certs)The first visit might show a security warning → click "Advanced" → "Proceed" (safe for local dev).

> ✅ Done! Your full app is running with zero manual setup.

