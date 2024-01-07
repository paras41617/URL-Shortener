
# URL Shortener

URL Shortener is a web app that allows users to create short links for their long URLs.
User can register on the web app and go the Shorten tab. There user can enter his/her long URL and get the short URL in response which is valid for 48 hours.
User can also go the Statistics tab and see all his/her links and their details.
The details include the original URL, short URL, it's creation date, it's expiration date and number of times it is clicked.

## Features

- Authentication
- URL Shortening
- Statistics

## Tech Stack

**Client:** Angular 14

**Server:** Flask, SQLAlchemy

**Database:** PostgreSQL

## Run Locally

Clone the project

```bash
  git clone https://github.com/paras41617/URL-Shortener.git
```

Go to the project directory

```bash
  cd url-shortener
```

Install dependencies For Backend

```bash
  cd backend
  pip install flask
  pip install shortuuid
  pip install flask_jwt_extended
  pip install flask_sqlalchemy
  pip install flask_cors 
```

Install dependencies For Frontend

```bash
  cd frontend
  npm install
```

Create a database in postgreSQL ( open postgres in your terminal by going to the username and then entering password) and update its credentials in the app.py file.

```bash
  CREATE DATABASE one;
```

Start backend

```bash
  python app.py
```

Start frontend

```bash
  ng serve
```
