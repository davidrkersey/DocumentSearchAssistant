# Document Search & Analysis Tool

## Overview

This is a **Streamlit-based web application** that allows users to **upload documents, search for specific terms**, and generate summaries. The application uses **OpenAI for text summarization** and **PostgreSQL as the database** to store processed data.

This guide will walk you through setting up and running the application using **Docker and Docker Compose**.

---

## Features

✅ Upload **PDF, Word, or Text files**\
✅ Search for **specific terms within documents**\
✅ Generate **AI-powered summaries** using OpenAI\
✅ Store and retrieve past searches using **PostgreSQL**\
✅ **Fully containerized** with Docker

---

## Prerequisites

Before running the application, ensure you have:

- **Docker** installed ([Download Here](https://www.docker.com/get-started))
- **Docker Compose** installed (included with Docker Desktop)
- An **OpenAI API key** ([Get one here](https://platform.openai.com/signup/))

---

## Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone <repository_url>
cd <repository_folder>
```

### 2️⃣ Add Your OpenAI API Key

Edit the `docker-compose.yml` file and \*\*replace \*\***`<your-api-key-here>`** with your actual **OpenAI API Key**:

```yaml
services:
  app:
    build:
      context: .
    ports:
      - "8501:8501"
    environment:
      DATABASE_URL: "postgresql://postgres:password@db:5432/mydatabase"
      OPENAI_API_KEY: "<your-api-key-here>"
    depends_on:
      db:
        condition: service_healthy
```

Alternatively, you can **set it manually** when running the app:

```bash
docker-compose up --build -e OPENAI_API_KEY=<your-api-key-here>
```

### 3️⃣ Start the Application

Run the following command to start the containers:

```bash
docker-compose up --build
```

This will:

- Start the **PostgreSQL database** (`db` service)
- Start the **Streamlit app** (`app` service)

### 4️⃣ Access the Application

Once the app is running, open your browser and go to:

```
http://localhost:8501
```
---

## Troubleshooting

### **"Could not translate hostname 'db' to address"**

- Ensure the **PostgreSQL container is running** by checking:
  ```bash
  docker ps
  ```
- If it’s not running, restart everything:
  ```bash
  docker-compose down && docker-compose up --build
  ```

### **"OpenAI API Key Not Found"**

- Ensure that your API key is set correctly in **docker-compose.yml**
- Alternatively, set it manually before running:
  ```bash
  export OPENAI_API_KEY=<your-api-key-here>
  docker-compose up --build
  ```

### **"Database Connection Error"**

- Ensure PostgreSQL is running:
  ```bash
  docker-compose ps
  ```
- Check logs for errors:
  ```bash
  docker-compose logs db
  ```

---

## Project Structure

```
/DocumentSearchAssistant
│── app.py               # Streamlit app
│── requirements.txt     # Python dependencies
│── Dockerfile           # Docker image definition
│── docker-compose.yml   # Docker Compose config
│── .dockerignore        # Ignore unnecessary files
│── utils/               # Utility functions
│   │── database.py      # Database connection
│   │── text_processor.py # Text processing
│   │── summarizer.py    # AI summarization
│── .streamlit/               # streamlit configs
│   │── config.toml      # toml to config
│── README.md            # This documentation
```

---

## Stopping the Application

To stop the running containers, press `CTRL+C` or run:

```bash
docker-compose down
```



 

