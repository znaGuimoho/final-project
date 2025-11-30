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
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── home.py             # Home page & listings
│   │   │   ├── hoster.py           # Host property management
│   │   │   └── more.py             # Additional pages (About, FAQ, etc.)
│   │   ├── services/
│   │   │   ├── Hash_password.py    # Password hashing utilities
│   │   │   └── user_service.py     # User management logic
│   │   └── static/
│   │       └── uploads/            # User-uploaded property images
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (not in git)
│   └── imgs.png                    # Sample image
│
├── frontend/
│   ├── css/                        # Stylesheets
│   │   ├── aboutUs.css
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
   SECRET_KEY=your-super-secret-key-change-this-in-production
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

## 🎨 Screenshots

> **Note**: Add screenshots of your application here to showcase the UI

```markdown
### Home Page
![Home Page](docs/screenshots/home.png)

### Property Listing
![login](docs/screenshots/login.png)

### Property Listing
![register](docs/screenshots/register.png)

### Host Dashboard
![Host Dashboard](docs/screenshots/host.png)
```

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