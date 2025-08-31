Library API

A Django REST Framework (DRF) project for managing users, books, orders, and a small community section with posts and comments.
Database powered by PostgreSQL.

🚀 Project Setup
1️⃣ Clone & Install
git clone <repo-url>
cd library-api
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
pip install -r requirements.txt

2️⃣ Environment Variables

Create .env file in the project root:

SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_NAME=library_db
DATABASE_USER=postgres
DATABASE_PASSWORD=yourpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432

3️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate

4️⃣ Start Server
python manage.py runserver


📦 Models Implemented

User (custom user model)

Book (title, author, price, stock, etc.)

Order (user, book, status, quantity)

Community

Post (title, body, author)

Comment (post, body, author)

🔗 API Endpoints
🔑 Auth

POST /auth/register/ → Register new user

POST /auth/login/ → Login & get token

📚 Books

GET /books/ → List all books

POST /books/ → Add a new book

GET /books/{id}/ → Retrieve single book

PUT /books/{id}/ → Update book

DELETE /books/{id}/ → Delete book