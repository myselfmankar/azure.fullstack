from flask import Flask, render_template, request, redirect, url_for, flash
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv
import os, uuid, logging

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)   # needed for flash messages

DATABASE_NAME  = "cloudDB"
CONTAINER_NAME = "users"

connection_string = os.getenv("DB_URI")
container = None

if not connection_string:
    log.error("DB_URI is missing from .env — Cosmos DB will not connect.")
else:
    try:
        client   = CosmosClient.from_connection_string(connection_string)
        database = client.create_database_if_not_exists(id=DATABASE_NAME)
        log.info(f"Database '{DATABASE_NAME}' ready.")

        try:
            container = database.create_container_if_not_exists(
                id=CONTAINER_NAME,
                partition_key=PartitionKey(path="/id"),
            )
        except exceptions.CosmosHttpResponseError as tp_err:
            log.warning(f"Default container creation failed ({tp_err.status_code}), "
                        "retrying with 400 RU/s dedicated throughput …")
            container = database.create_container_if_not_exists(
                id=CONTAINER_NAME,
                partition_key=PartitionKey(path="/id"),
                offer_throughput=400,
            )

        log.info(f"Container '{CONTAINER_NAME}' ready.")

    except Exception as e:
        log.error(f"Cosmos DB initialisation failed: {e}")
        container = None


@app.route("/")
def home():
    users = []
    if container:
        try:
            items = list(container.read_all_items())
            users = [(item["id"], item.get("name", "")) for item in items]
        except Exception as e:
            log.error(f"Failed to fetch users: {e}")
            flash("Could not load users from the database.", "error")
    else:
        flash("Database not connected. Check your .env file.", "error")
    return render_template("index.html", users=users)


@app.route("/save", methods=["POST"])
def save():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Name cannot be empty.", "error")
        return redirect(url_for("home"))
    if not container:
        flash("Database not connected.", "error")
        return redirect(url_for("home"))
    try:
        container.upsert_item({"id": str(uuid.uuid4()), "name": name})
        log.info(f"User '{name}' added.")
    except Exception as e:
        log.error(f"Save failed: {e}")
        flash("Failed to add user.", "error")
    return redirect(url_for("home"))


@app.route("/update/<id>", methods=["POST"])
def update(id):
    name = request.form.get("name", "").strip()
    if not name:
        flash("Name cannot be empty.", "error")
        return redirect(url_for("home"))
    if not container:
        flash("Database not connected.", "error")
        return redirect(url_for("home"))
    try:
        item = container.read_item(item=id, partition_key=id)
        item["name"] = name
        container.upsert_item(item)
        log.info(f"User {id[:8]}… updated to '{name}'.")
    except exceptions.CosmosResourceNotFoundError:
        log.warning(f"Update skipped — user {id[:8]}… not found.")
        flash("User not found.", "error")
    except Exception as e:
        log.error(f"Update failed: {e}")
        flash("Failed to update user.", "error")
    return redirect(url_for("home"))


@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    if not container:
        flash("Database not connected.", "error")
        return redirect(url_for("home"))
    try:
        container.delete_item(item=id, partition_key=id)
        log.info(f"User {id[:8]}… deleted.")
    except exceptions.CosmosResourceNotFoundError:
        log.warning(f"Delete skipped — user {id[:8]}… not found.")
    except Exception as e:
        log.error(f"Delete failed: {e}")
        flash("Failed to delete user.", "error")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)