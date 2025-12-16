# 🏠 House Renting Platform

A modern, full-stack house renting platform that connects property hosts with potential renters. Built with **FastAPI** (Python) and **PostgreSQL**, featuring secure authentication, image uploads, and an intuitive user interface.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-supported-2496ED?style=for-the-badge&logo=docker)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### For Renters
- 🔍 **Browse Listings** – View available properties with photos and detailed information
- ⭐ **Save Favorites** – Bookmark properties you're interested in
- 📱 **Responsive Design** – Seamless experience across all devices
- 💡 **Rental Tips** – Access helpful guides for first-time renters

### For Hosts
- 📤 **Easy Property Upload** – Add listings with multiple photos
- 🖼️ **Image Management** – Upload and manage property images
- 📊 **Host Dashboard** – Manage all your listings in one place
- ✅ **Quick Setup** – Get your property listed in minutes

### Platform Features
- 🔐 **Secure Authentication** – Session-based login system
- 📧 **Contact System** – Direct communication channels
- 📜 **Legal Pages** – Terms & Conditions, FAQs
- 🎨 **Modern UI** – Clean, intuitive interface

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL 15 |
| **Authentication** | Session-based with secure cookies |
| **File Storage** | Local filesystem |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Security** | SSL/TLS (HTTPS), Password hashing |
| **Deployment** | Docker + Docker Compose |

---

## 📊 Database Schema

### Overview
The platform uses PostgreSQL to manage user authentication, house listings, favorites, contact history, and session management. Below is the complete database structure.

### Quick Stats
- **9 Database Objects**: 6 tables + 3 sequences
- **Foreign Key Relationships**: 8 constraints ensuring data integrity
- **JSON Fields**: For flexible data storage (house details, user activity)

---

## Tables

### 1. users
Stores user account information with authentication credentials.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| user_name | VARCHAR(100) | NOT NULL | User's display name |
| email | VARCHAR(150) | NOT NULL, UNIQUE | User's email address |
| hashed_password | TEXT | NOT NULL | Hashed password for authentication |
| salt | TEXT | NOT NULL | Salt used for password hashing |
| banned | BOOLEAN | DEFAULT false | Account ban status |

**Create Query:**
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    salt TEXT NOT NULL,
    banned BOOLEAN DEFAULT false
);
```

---

### 2. houses
Contains house rental listings with details and location information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique house identifier |
| category | VARCHAR(50) | | House category/type |
| price | NUMERIC(10,2) | | Rental price |
| location_name | VARCHAR(255) | | Human-readable location |
| location_url | VARCHAR(255) | | Map/location URL |
| img_url | TEXT | | House image URL |
| details | JSON | | Additional house details (JSON format) |

**Create Query:**
```sql
CREATE TABLE houses (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    price NUMERIC(10,2),
    location_name VARCHAR(255),
    location_url VARCHAR(255),
    img_url TEXT,
    details JSON
);
```

---

### 3. myfavorite
Junction table linking users to their favorite house listings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| house_id | INTEGER | FOREIGN KEY → houses(id) | Reference to house |
| user_id | INTEGER | FOREIGN KEY → users(user_id) | Reference to user |

**Constraints:**
- Unique constraint on (house_id, user_id) to prevent duplicates
- CASCADE delete when house or user is deleted

**Create Query:**
```sql
CREATE TABLE myfavorite (
    house_id INTEGER,
    user_id INTEGER,
    CONSTRAINT myfavorite_unique_user_house UNIQUE (house_id, user_id),
    CONSTRAINT fk_house FOREIGN KEY (house_id) REFERENCES houses(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

---

### 4. contact_history
Tracks communication between users and house hosts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| room_name | VARCHAR(255) | NOT NULL | Chat room/conversation identifier |
| house_id | INTEGER | NOT NULL, FOREIGN KEY → houses(id) | House being inquired about |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(user_id) | User making contact |
| hoster_id | INTEGER | NOT NULL, FOREIGN KEY → users(user_id) | House owner/host |

**Create Query:**
```sql
CREATE TABLE contact_history (
    room_name VARCHAR(255) NOT NULL,
    house_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    hoster_id INTEGER NOT NULL,
    CONSTRAINT contact_history_house_id_fkey FOREIGN KEY (house_id) REFERENCES houses(id),
    CONSTRAINT contact_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT contact_history_hoster_id_fkey FOREIGN KEY (hoster_id) REFERENCES users(user_id)
);
```

---

### 5. sessions
Manages user authentication sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| session_id | UUID | PRIMARY KEY | Unique session identifier |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(user_id) | User associated with session |
| created_at | TIMESTAMP | DEFAULT now() | Session creation time |
| expires_at | TIMESTAMP | | Session expiration time |

**Create Query:**
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

---

### 6. user_data
Stores user activity data in JSON format.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique record identifier |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(user_id) | User reference |
| visited | JSONB | DEFAULT '[]' | Array of visited houses |
| history | JSONB | DEFAULT '{}' | User browsing/activity history |

**Create Query:**
```sql
CREATE TABLE user_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    visited JSONB DEFAULT '[]'::jsonb,
    history JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT user_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

---

## Entity Relationships

```
users (1) ──→ (N) sessions
users (1) ──→ (N) myfavorite
users (1) ──→ (N) contact_history [as user]
users (1) ──→ (N) contact_history [as hoster]
users (1) ──→ (1) user_data

houses (1) ──→ (N) myfavorite
houses (1) ──→ (N) contact_history
```

---

## Indexes

- `users_pkey`: PRIMARY KEY on users(user_id)
- `users_email_key`: UNIQUE on users(email)
- `houses_pkey`: PRIMARY KEY on houses(id)
- `myfavorite_unique_user_house`: UNIQUE on myfavorite(house_id, user_id)
- `sessions_pkey`: PRIMARY KEY on sessions(session_id)
- `user_data_pkey`: PRIMARY KEY on user_data(id)

---

## Complete Database Setup

```sql
-- Create all tables in order (respecting foreign key dependencies)

-- 1. Create users table first (no dependencies)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    salt TEXT NOT NULL,
    banned BOOLEAN DEFAULT false
);

-- 2. Create houses table (no dependencies)
CREATE TABLE houses (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    price NUMERIC(10,2),
    location_name VARCHAR(255),
    location_url VARCHAR(255),
    img_url TEXT,
    details JSON
);

-- 3. Create dependent tables
CREATE TABLE myfavorite (
    house_id INTEGER,
    user_id INTEGER,
    CONSTRAINT myfavorite_unique_user_house UNIQUE (house_id, user_id),
    CONSTRAINT fk_house FOREIGN KEY (house_id) REFERENCES houses(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE contact_history (
    room_name VARCHAR(255) NOT NULL,
    house_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    hoster_id INTEGER NOT NULL,
    CONSTRAINT contact_history_house_id_fkey FOREIGN KEY (house_id) REFERENCES houses(id),
    CONSTRAINT contact_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT contact_history_hoster_id_fkey FOREIGN KEY (hoster_id) REFERENCES users(user_id)
);

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE user_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    visited JSONB DEFAULT '[]'::jsonb,
    history JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT user_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

## 📁 Project Structure

```
finalProject/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── cert.pem                # SSL certificate (development)
│   │   ├── key.pem                 # SSL private key (development)
│   │   ├── routers/
|   |   |   ├── contact.py          # contact managment
|   |   |   ├── favorites.py        # favorite managment
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── home.py             # Home page & listings
│   │   │   ├── hoster.py           # Host property management
│   │   │   └── more.py             # Additional pages (About, FAQ, etc.)
│   │   ├── services/
|   |   |   ├── conatct_servises.py
|   |   |   ├── redis_db.py
│   │   │   ├── Hash_password.py    # Password hashing utilities
│   │   │   └── user_service.py 
│   │   ├── events/
|   |   |   └──contact_events.py 
│   └── static/
│       └── uploads/                # User-uploaded property images
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (not in git)
│   └── imgs.png                    # Sample image
│
├── frontend/
│   ├── css/                        # Stylesheets
│   │   ├── aboutUs.css
│   │   ├── contact.css
│   │   ├── favorite.css
│   │   ├── house.css
│   │   ├── base.css
│   │   ├── home.css
│   │   ├── host.css
│   │   ├── login.css
│   │   ├── register.css
│   │   ├── rentalTips.css
│   │   ├── termsAndConditions.css
│   │   └── uploadSuccess.css
│   ├── imgs/                       # Static images
│   │   ├── house.png
│   │   ├── logo-home-png-7429.png
│   │   ├── Me.png
│   │   ├── menu.png
│   │   ├── photo-for-more.png
│   │   ├── profile.png
│   │   ├── sekectedStar.png
│   │   ├── star.png
│   │   └── photo-for-more.jpeg
│   ├── scripts/                    # JavaScript modules
│   │   ├── home.js
│   │   ├── login.js
│   │   ├── register.js
│   │   ├── host.js
│   │   ├── aboutUs.js
│   │   ├── rentalTips.js
│   │   ├── terms.js
│   │   └── uploadSuccess.js
│   └── *.html                      # HTML pages
│
├── docker-compose.yml              # Multi-container orchestration
├── Dockerfile                      # Backend container definition
├── .gitignore                      # Git exclusions
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

Choose one of the following:

**Option A: Docker (Recommended)**
- [Docker Desktop](https://www.docker.com/get-started) or Docker Engine + Docker Compose

**Option B: Manual Setup**
- Python 3.11 or higher
- PostgreSQL 15 or higher
- pip (Python package manager)

### Installation

#### Using Docker (Easiest - One Command!)

1. **Clone the repository**
   ```bash
   git clone https://github.com/znaGuimoho/finalProject.git
   cd finalProject
   ```

2. **Configure environment variables**
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` with your settings:
   ```env
   DATABASE_URL=postgresql://postgres:password@db:5432/house_renting
   ```

3. **Launch the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the platform**
   
   Open your browser and navigate to:
   ```
   https://localhost:8000
   ```
   
   > ⚠️ **First-time SSL warning**: Your browser will show a security warning because we're using self-signed certificates for local development. Click "Advanced" → "Proceed to localhost" (this is safe for local development).

#### Manual Setup (Without Docker)

1. **Clone and navigate**
   ```bash
   git clone https://github.com/znaGuimoho/finalProject.git
   cd finalProject
   ```

2. **Set up PostgreSQL database**
   ```bash
   createdb house_renting
   ```

3. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile app/key.pem --ssl-certfile app/cert.pem
   ```

---

## 📖 API Documentation

Once the server is running, visit:

- **Interactive API Docs (Swagger)**: https://localhost:8000/docs
- **Alternative Docs (ReDoc)**: https://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Create new user account |
| `/auth/login` | POST | User login |
| `/auth/logout` | POST | User logout |
| `/home/listings` | GET | Fetch all property listings |
| `/host/upload` | POST | Upload new property listing |
| `/host/properties` | GET | Get host's properties |

---

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=your-secret-key-min-32-characters-long

# Application
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# File Upload
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
UPLOAD_DIR=app/static/uploads
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# Rebuild containers
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Access database
docker-compose exec db psql -U postgres -d house_renting
```

---

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## 🛣️ Roadmap

- [ ] Add property search and filtering
- [ ] Implement booking system
- [ ] Add payment integration
- [ ] Create mobile app
- [ ] Add real-time messaging between hosts and renters
- [ ] Implement review and rating system
- [ ] Add email notifications
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**

- GitHub: [@znaGuimoho](https://github.com/znaGuimoho)
- Project Link: [https://github.com/znaGuimoho/finalProject](https://github.com/znaGuimoho/finalProject)

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- PostgreSQL for reliable data storage
- Docker for simplifying deployment
- All contributors who help improve this project

---

<div align="center">

**[⬆ Back to Top](#-house-renting-platform)**

Made with ❤️ by [znaGuimoho](https://github.com/znaGuimoho)

</div>