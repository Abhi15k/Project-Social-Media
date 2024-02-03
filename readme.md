# Social Media FastAPI

This FastAPI project implements user authentication with OAuth2, user sign-up, login, and post creation functionality for a social media application. It utilizes SQLAlchemy for database management and Alembic for database migrations.

## Prerequisites

Before you begin, ensure you have the following requirements:

- Python 3.x installed
- [pip](https://pip.pypa.io/en/stable/installation/) installed
- Sqlite3 server running (adjust connection details in `database.py` if needed)

## Getting Started

1. **Clone the repository:**

```bash
git clone https://github.com/Abhi15k/Project-Social-Media.git
```

2. **Navigate to the project directory:**

```bash
  cd Project-Social-Media
```

3. **Create a virtual environment:**

```bash
python -m venv venv
```

4. **Activate the virtual environment:**
   On Windows:

   ```bash
    .\venv\Scripts\activate
   ```

   On macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

5. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

   ```

6. **Database setup:**

   Update the database connection string in `database.py` if needed.

   Apply database migrations:

   ```bash
   alembic upgrade head
   ```

7. **Run the FastAPI application:**

   ```bash
   uvicorn main:app --reload
   ```

   Open your browser and go to http://127.0.0.1:8000/docs to interact with the Swagger documentation.

8. **Test the Endpoints:**

   -Use tools like curl or Postman to test the API endpoints, or you can use the Swagger documentation interface.

   -while testing pass the values in JASON for 'signup/' in postman and for '/login' pass values in x-www-form-urlencoded

   -while testing the '/posts/' Please use Authorization in header "Bearer <Your login token>" (Note:"For security here tokenization is done so without token you cannot post. Token will automatically generate after login")

9. **Shutdown the application:**
   <br>Press Ctrl + C in the terminal to stop the running FastAPI application.

10. **Deactivate the virtual environment:**

    ```bash
        deactivate
    ```

11. **Usage**

    -Sign up using the /signup/ endpoint.<br>
    -Log in using the /login endpoint to obtain an access token.<br>
    -Use the access token to create posts using the /posts/ endpoint.<br>
    -List users with the /users/ endpoint.<br>
    -List recent posts with the /recent_posts/ endpoint.<br>

12. **Troubleshooting**

If you encounter any issues, please check:

    -Ensure all dependencies are installed correctly.
    -Verify that the database connection is configured properly.
    -Check the logs for any error messages.
