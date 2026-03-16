# Azure Full Stack App

A full-stack CRUD application built with **Flask** and **Azure Cosmos DB (NoSQL API)**, deployed on an **Azure Virtual Machine**.

---

## Tech Stack

- **Backend** — Python / Flask
- **Database** — Azure Cosmos DB (NoSQL / SQL API)
- **Server** — Azure VM (Ubuntu)

---

## Connecting to Azure Cosmos DB

### 1. Create a Cosmos DB Account

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **Azure Cosmos DB** → **Create**
3. Select API: **Azure Cosmos DB for NoSQL**
4. Choose your subscription and resource group
5. Give it an account name and click **Review + Create**

### 2. Get the Connection String

1. Open your Cosmos DB account in the portal
2. In the left menu go to **Settings → Keys**
3. Copy the **PRIMARY CONNECTION STRING** — it looks like:

```
AccountEndpoint=https://<your-account>.documents.azure.com:443/;AccountKey=<your-key>;
```

### 3. Configure the App

Create a `.env` file in the project root:

```env
DB_URL="AccountEndpoint=https://<your-account>.documents.azure.com:443/;AccountKey=<your-key>;"
```

> The database (`cloudDB`) and container (`users`) are created automatically on first run if they don't already exist.

---

## Running the App

```bash
pip install -r requirements.txt
python app.py
```

The app will be available at `http://127.0.0.1:5000`

---

## Deploying on Azure VM

1. SSH into your VM
2. Clone this repo and `cd` into it
3. Create the `.env` file with your `DB_URL` as shown above
4. Install dependencies and run:

```bash
pip install -r requirements.txt
python app.py
```
