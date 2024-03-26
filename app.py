import requests
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from flask import request, jsonify
from google.oauth2.credentials import Credentials

from flask import Flask, request
from google.api_core.exceptions import BadRequest
import requests
import PyPDF2
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text_to_fp
from pdfminer.high_level import extract_text
import glob
import docx2txt
import iso8601  # This library helps to parse datetime strings to datetime objects
import shutil
import zipfile
import logging
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from flask import Flask, request, render_template, send_file
from datetime import datetime
import time
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    Response,
)

import os
from datetime import datetime
import weaviate
import openai
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
from google.oauth2 import service_account
import json
import io
import re
import threading
import random
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import secrets
import uuid
from dotenv import load_dotenv
import ast
import fitz  # PyMuPDF
import os
import shutil
import json

app = Flask(__name__)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


mail = Mail(app)
app.secret_key = "JobBot"

global lm_client
global layer_1 
global loading_status

loading_status = None

import tracemalloc

tracemalloc.start()


load_dotenv()


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587  # Use 465 for SSL
app.config["MAIL_USERNAME"] = "iamkamrankhan00@gmail.com"  # Ensure correct email
app.config["MAIL_PASSWORD"] = "zjwj qhxq askj mxbh"
app.config["MAIL_USE_TLS"] = True  # Set to False if using SSL
app.config["MAIL_USE_SSL"] = False  # Set to True if using SSL


mail.init_app(app)

global audio_speech
audio_speech = None

global projectName
projectName = "Bot"

global p1
p1 = "provide the answer only in the context of Capria Global  South Fund II"

global p2
p2 = "provide the answer only in the context of Capria Global  South Fund II"

global stop_flag
stop_flag = False

global citations_dictt


def readAndWriteJsonData(path, mode, data=None):
    if mode == "r":
        try:
            with open(path, "r") as file:
                json_data = json.load(file)
            return json_data
        except FileNotFoundError:
            print(f"File '{path}' not found.")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from '{path}'.")
            return None
    elif mode == "w":
        try:
            with open(path, "w") as file:
                json.dump(data, file, indent=4)
            print(f"Data written to '{path}' successfully.")
        except Exception as e:
            print(f"Error writing data to '{path}': {e}")
    else:
        print("Invalid mode. Use 'r' for reading or 'w' for writing.")

def generate_google_drive_url(file_id):
    return f"http://drive.google.com/file/d/{file_id}/view"


@app.route("/send_verification", methods=["POST"])
def send_verification():
    data = request.get_json()  
    email = data.get("email")
    if not email:
        return jsonify({"message": "No email provided"}), 400

    otp = random.randint(100000, 999999)
    session[email] = otp
    print(otp, "otp sent ")

    msg = Message(
        "Email Verification", sender="iamkamrankhan00@gmail.com", recipients=[email]
    )
    msg.body = f"Your verification code is: {otp}"
    mail.send(msg)

    return jsonify({"message": "Verification email sent"})


def replace_in_string(text):
    chars_to_replace = ["\\", "/", "_"]
    for char in chars_to_replace:
        text = text.replace(char, " ")
    text = text.replace(".png", "")
    return text


@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    print(otp, "otp ")
    stored_otp = session.get(email)
    print(stored_otp, "stored_otp")

    if stored_otp and str(stored_otp) == str(otp):
        return jsonify({"message": "Email verified successfully"})
    else:
        return jsonify({"message": "Invalid or expired OTP"}), 400


key = os.getenv("SECRET_KEY")

# lm_client = openai.OpenAI(api_key=key)
service_account_file = "cred.json"
credentials = service_account.Credentials.from_service_account_file(
    service_account_file
)
dbclient = bigquery.Client(credentials=credentials, project=credentials.project_id)
credentials_path = "credentials.json"
response = "Done."
app.secret_key = "secret_key"

global intro
intro = """
Welcome to the alpha version of Capria's DD Copilot. Trying asking "What is the MOFC for Betterplace" or "Does Capria invest in genai infrastructure?" or "Does Capria consider DEI" or "Who is Capria's tax advisor"
"""


def add_row_to_sheet(data, sheet_id):
    creds = Credentials.from_service_account_file(
        credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)

    try:
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)
        worksheet.append_row(data)
        print("Row added successfully!")
    except Exception as e:
        print("Error: ", e)


from google.cloud import bigquery


def get_user_by_userID(userID):
    try:

        dataset_name = "my-project-41692-400512.jobbot"
        table_name = "users"

        query = """
            SELECT *
            FROM `{0}.{1}`
            WHERE userID = @userID
        """.format(
            dataset_name, table_name
        )

        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("userID", "STRING", userID)]
        )

        query_job = dbclient.query(query, job_config=job_config)  # Make an API request

        results = query_job.result()  # Waits for job to complete

        for row in results:
            return {
                "name": row.name,
                "password": row.password,
                "userID": row.userID,
                "isAnswer": row.isAnswer,
                "role": row.role,
            }

        return None

    except Exception as e:
        print(f"An error occurred while retrieving user: {str(e)}")
        return None


@app.route("/control_panel", methods=["GET", "POST"])
def control_panel():
    global intro, projectName, p1, p2

    config_data = {}
    config_data1 = {}

    # Load configuration for GET request
    if request.method == "GET":
        if os.path.exists("config.json"):
            with open("config.json", "r") as file:
                config_data = json.load(file)

        if os.path.exists("config1.json"):
            with open("config1.json", "r") as file:
                config_data1 = json.load(file)

    if request.method == "POST":
        session["language"] = request.form.get("language", "english")
        session["language"] = get_language(session["language"])
        projectName = request.form.get("title", "Bot")
        session["intro"] = request.form.get("intro", "")
        intro = session["intro"] if session["intro"] != "" else intro

        p1 = request.form.get("prompt_level1", "")
        p2 = request.form.get("prompt_level2", "")

    print("\n\nLanguage being retuned:", session["language"], "\n\n")
    userID = session["userID"]
    user = get_user_by_userID(userID)
    # print("users---------", user)
    role = user["role"]

    return render_template(
        "control_panel.html",
        language=session.get("language", "english"),
        intro=intro,
        prompt_level1=p1,
        prompt_level2=p2,
        prompt_level3=p1,
        role=role,
        name=projectName,
        config_data=config_data,
        config_data1=config_data1,
    )


@app.route("/trans")
def trans():
    global intro, projectName
    newList = []
    transwords = [
        projectName,
        "User",
        "Enter Your Query",
        "Feedback",
        "Fast Mode",
        intro,
        "Check level 2?",
        "Submit",
        "Close",
        "Slow Mode",
        "Groq Mode",
    ]

    if session["language"] == "null":
        session["language"] = "en"

    if session["language"] != "en":
        for item in transwords:
            trans = translate_text(item, session["language"])
            print(trans, "transscripted words ")
            newList.append(trans)

    if not newList:
        newList = transwords

    return jsonify(newList)


@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    try:
        audio_file = request.files["audioFile"]
        if audio_file:
            audio_bytes = audio_file.read()
            audio_file = FileWithNames(audio_bytes)
            session["greet"], session["language"] = transcribe(audio_file)
            session["language"] = (
                request.form["language"]
                if request.form["language"] != "auto"
                else session["language"]
            )
            session["language"] = get_language(session["language"])
            print("\n\n\n", session["language"], "\n\n\n")

            print("\n\n\n", session["language"], "\n\n\n")
    except Exception as e:
        print(e)
        update_logs(e)
        session["language"] = "english"

    return jsonify({"channel": "chat"})


@app.route("/chat")
def chat():
    if "language" not in session or session["language"] is None:
        session["language"] = "en"
        print("Language set to English")
    userID = session["userID"]
    user = get_user_by_userID(userID)
    # print("users---------", user)
    role = user["role"]
    print("Redirecting...")
    return render_template("chat.html", role=role)


@app.route("/")
def index():
    return render_template("login.html")


custom_functions = [
    {
        "name": "return_response",
        "description": "Function to be used to return the response to the question, and a boolean value indicating if the information given was suffieicnet to generate the entire answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "item_list": {
                    "type": "array",
                    "description": "List of chunk ids. ONLY the ones used to generate the response to the question being asked. return the id only if the info was used in the response. think carefully.",
                    "items": {"type": "integer"},
                },
                "response": {
                    "type": "string",
                    "description": "This should be the answer that was generated from the context, given the question",
                },
                "sufficient": {
                    "type": "boolean",
                    "description": "This should represent wether the information present in the context was sufficent to answer the question. Return True is it was, else False.",
                },
            },
            "required": ["response", "sufficient", "item_list"],
        },
    }
]

custom_functions_1 = [
    {
        "name": "return_response",
        "description": "Function to be used to return the response to the question, and a boolean value indicating if the information given was suffieicnet to generate the entire answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "boolean",
                    "description": "This should be the answer that was generated from the context, given the question",
                },
                "sufficient": {
                    "type": "boolean",
                    "description": "This should represent wether the information present in the context was sufficent to answer the question. Return True is it was, else False.",
                },
            },
            "required": ["response", "sufficient"],
        },
    }
]

import time

custom_functionsz = [
    {
        "name": "return_response",
        "description": "Function to be used to return the response to the question, and a boolean value indicating if the information given was suffieicnet to generate the entire answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "response_answer": {
                    "type": "string",
                    "description": "This should be the answer that was generated from the context, given the question",
                },
                "item_list": {
                    "type": "array",
                    "description": "List of chunk ids. ONLY the ones used to generate the response to the question being asked. return the id only if the info was used in the response. think carefully.",
                    "items": {"type": "integer"},
                },
                "sufficient": {
                    "type": "boolean",
                    "description": "This should represent wether the information present in the context was sufficent to answer the question. Return True is it was, else False.",
                },
            },
            "required": ["response_answer", "sufficient", "item_list"],
        },
    }
]


def ask_gpt(
    question,
    context,
    gpt,
    metadata,
    language,
    addition,
    userid,
    filename="Layer_1_file/file_info_1.json",
):
    global audio_speech, stop_flag, citations_dictt
    user_message = "Question: \n\n" + question + "\n\n\nContext: \n\n" + context
    system_message = "You will be given context from several pdfs, this context is from several chunks, rettrived from a vector DB. each chunk will have a chunk id above it. You will also be given a question. Formulate an answer, ONLY using the context, and nothing else. provide in-text citations within square brackets at the end of each sentence, right after each fullstop. The citation number represents the chunk id that was used to generate that sentence. Do Not bunch multiple citations in one bracket. Uee seperate brackets for each digit. {} Return the response along with a boolean value indicating if the information from the context was enough to answer the question. Return true if it was, False if it wasnt. Return the response, which is th answer to the question asked".format(
        addition
    )

    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    response = lm_client.chat.completions.create(
        model=gpt,
        messages=msg,
        max_tokens=500,
        temperature=0.0,
        functions=custom_functionsz,
        function_call="auto",
        stream=True,
    )

    string = ""
    response_answer = ""
    item_list = ""
    sufficient = ""

    for chunk in response:
        try:
            delta = chunk.choices[0].delta.function_call.arguments
            string += delta
            if '"item_list":' in string:
                item_list = string.split('"item_list":')[1]
            elif '"response_answer":' in string:
                response_answer = string.split('"response_answer":')[1]

            data = {
                "response": response_answer,
                "sufficient": False,
                "endOfStream": stop_flag,
            }
            stop_flag = False
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"
        except Exception as e:
            print(
                "\n\n\n--------------------------------------------------------------------------------"
            )
            print(e)
            print(chunk)
            print(
                "--------------------------------------------------------------------------------\n\n\n"
            )

            continue

    item_list = item_list.split(",\n")[0]
    print(item_list.strip())
    item_list = ast.literal_eval(item_list.strip())
    response = response_answer.replace('"item_list', "")

    # response = translate_text(response, language) if language != "en" else response
    # audio_speech = lm_client.audio.speech.create(
    #     model="tts-1", voice="alloy", input=response
    # )
    # filename = str(userid) + ".mp3"
    # audio_speech.stream_to_file(filename)

    # Load the JSON data from the file
    with open(filename, "r") as file:
        files_metadata = json.load(file)

    try:
        cits = ["www.google.com"] * (max(item_list) + 4)
        for item in item_list:
            response += "\n"
            response += "[{}]".format(item)
            response += replace_in_string(metadata[item - 1])
            for filedata in files_metadata:
                name = filedata["name"].split(".docx")[0]
                name = filedata["name"].split(".pptx")[0]
                name = filedata["name"].split(".pdf")[0]
                file_id = filedata["id"]
                if name in metadata[item - 1]:
                    cits[item] = generate_google_drive_url(file_id)

        lst = "\n\n\n list_of_citations = " + str(cits)
        lst = lst.replace("'", '"')
        response += lst
    except:
        pass

    # print(response)
    data = {"response": response, "sufficient": False, "endOfStream": True}
    json_data = json.dumps(data)
    yield f"data: {json_data}\n\n"


def qdb(query, db_client, name, cname, chunk_id, limit):
    context = None
    metadata = []
    try:
        res = (
            db_client.query.get(name, ["text", "metadata"])
            .with_near_text({"concepts": query})
            .with_limit(limit)
            .do()
        )
        print(res, "response from qdb")
        context = ""
        metadata = []
        for i in range(limit):
            context += "Chunk ID: " + str(chunk_id) + "\n"
            context += res["data"]["Get"][cname][i]["text"] + "\n\n"
            met = res["data"]["Get"][cname][i]["metadata"]
            metadata.append(met.split(".png")[0])
            chunk_id += 1
    except Exception as e:
        print("Exception in DB, dude.")
        print(e)
        time.sleep(3)
        context, metadata = qdb(query, db_client, name, cname, chunk_id, limit)
    return context, metadata


def check_email_exists(email):
    table_id = "my-project-41692-400512.jobbot.users"
    query = """
    SELECT * 
    FROM `{}`
    WHERE email = @email
    """.format(
        table_id
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email),
        ]
    )

    query_job = dbclient.query(query, job_config=job_config)

    results = list(query_job.result())
    return len(results) > 0


def insert_user_data(name, password, email, userID):
    table_id = "my-project-41692-400512.jobbot.users"

    rows_to_insert = [
        {
            "name": name,
            "password": password,
            "email": email,
            "userID": userID,
            "role": "user",
            "isAnswer": False,
            "iswhiteList": False,
        }
    ]

    errors = dbclient.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))


# insert_user_data('sumat','password','s@email.com','asdfwzx234f234asf')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        userID = str(uuid.uuid4())
        name = request.form.get("name")
        password = request.form.get("password")
        email = request.form.get("email")

        if not name or not password:
            print("Name or password not provided")  # Debugging line
            message = "Name and password are required."
            return render_template("signup.html", message=message)

        if check_email_exists(email):
            print("Name already exists")  # Debugging line
            message = "User already exists."
            return render_template("signup.html", message=message)

        hashed_password = generate_password_hash(password)
        insert_user_data(name, password, email, userID)
        print("User registered successfully")  # Debugging line
        return redirect(url_for("login"))

    return render_template("signup.html")


def update_password(email, new_password):
    hashed_password = generate_password_hash(new_password)

    client = dbclient

    table_id = "my-project-41692-400512.1234.jobbot.users"

    query = f"""
    UPDATE `{table_id}`
    SET password = @new_password
    WHERE email = @email
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("new_password", "STRING", new_password),
            bigquery.ScalarQueryParameter("email", "STRING", email),
        ]
    )

    query_job = client.query(query, job_config=job_config)  # Make an API request.

    query_job.result()

    return "Password updated successfully."


@app.route("/update_password", methods=["GET", "POST"])
def handle_update_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")

        response = update_password(email, new_password)

        return redirect(
            url_for("login")
        )  # Assuming 'login' is the endpoint for your login page

    return render_template("reset_password.html")


def get_user_by_username(name):
    dataset_name = "my-project-41692-400512.jobbot"
    table_name = "users"

    query = """
        SELECT *
        FROM `{0}.{1}`
        WHERE name = @name
    """.format(
        dataset_name, table_name
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", name)]
    )

    query_job = dbclient.query(query, job_config=job_config)

    results = query_job.result()

    for row in results:
        return {
            "name": row.name,
            "password": row.password,
            "userID": row.userID,
            "isAnswer": row.isAnswer,  # Corrected attribute name
            "role": row.role,
            "isWhiteList": row.iswhiteList,  # Corrected attribute name
        }

    return None

def add_to_whitelist(name, email, userID):
    table_id = "my-project-41692-400512.jobbot.whitelisted_users"

    rows_to_insert = [
        {
            "name": name,
            "email": email,
            "userID": userID,
        }
    ]

    errors = dbclient.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
    if errors == []:
        print("User added to whitelist successfully.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            name = request.form["name"]
            password = request.form["password"]

            user = get_user_by_username(name)

            if user and password == user["password"]:
                session["userID"] = user["userID"]
                session["language"] = "en"
                session.modified = True

                if user["isWhiteList"]:
                    return redirect("/chat")
                else:
                    return render_template(
                        "login.html",
                        message="You are not allowed to login. Please contact the admin.",
                    )
            else:
                return "Invalid username or password", 401
        except Exception as e:
            print(e, "error in login")
            return f"Error: {e}", 500
    return render_template("login.html")


@app.route("/forgot_password", methods=["GET"])
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    try:
        unique_id = data.get("uniqueId")
        thumbs = data.get("type", "Text")
        l2 = data.get("l2ResponseClicked")
        l3 = data.get("l3ResponseClicked")
        feedback_text = data.get("feedback", "Null")
        level = data.get("level", "test")
        print(thumbs, feedback_text, level)
        if not l2 and not l3:
            add_row_to_sheet(
                [
                    session["transcription"],
                    session["level_1_response"],
                    thumbs,
                    feedback_text,
                ],
                "1OvOj468hgwhjrBFqWrHrZtSirrodrUEejBUUr37by_Y",
            )
        if l2 and not l3:
            add_row_to_sheet(
                [
                    session["transcription"],
                    session["level_2_response"],
                    thumbs,
                    feedback_text,
                ],
                "1OvOj468hgwhjrBFqWrHrZtSirrodrUEejBUUr37by_Y",
            )
        if l2 and l3:
            add_row_to_sheet(
                [
                    session["transcription"],
                    session["level_3_response"],
                    thumbs,
                    feedback_text,
                ],
                "1OvOj468hgwhjrBFqWrHrZtSirrodrUEejBUUr37by_Y",
            )
    except Exception as e:
        update_logs(e)

    return jsonify({"status": "success"})


def transcribe(audio_file):
    try:
        response = lm_client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="verbose_json"
        )
        transcription = response.text
        language = response.text + " " + response.language
    except Exception as e:
        print(e)
        update_logs(e)
        transcription = "Error."
        language = "english"

    return transcription, language


class FileWithNames(io.BytesIO):
    name = "audio.wav"


def update_logs(input_string):
    file_exists = os.path.isfile("logs.txt")

    with open("logs.txt", "a" if file_exists else "w") as file:
        if file_exists:
            file.write("\n\n\n\n")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{current_time}\n{input_string}\n")


def process_response(input_string, replacements):
    def replacement(match):
        index = int(match.group(1))
        return (
            f"[{replacements[index]}]" if index < len(replacements) else match.group(0)
        )

    try:
        return re.sub(r"\[(\d+)\]", replacement, input_string)
    except:
        return input_string


import requests


def translate_text(text, target_language):
    print(target_language)
    api_key = "AIzaSyAtfrkxLhTygIJi9Rb-l0duA8fV9LgKZ7M"  # Replace with your API key

    url = "https://translation.googleapis.com/language/translate/v2"
    data = {"q": text, "target": target_language, "format": "text"}
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    response = requests.post(url, headers=headers, params=params, json=data)
    r = response.json()
    print(r)
    return r["data"]["translations"][0]["translatedText"]


def get_language(lang):
    print("getting lang.")
    lang = lang.lower()
    if "arabic" in lang:
        return "ar"
    if "kannada" in lang:
        return "kn"
    if "telugu" in lang:
        return "te"
    if "spanish" in lang:
        return "es"
    if "hebrew" in lang:
        return "he"
    if "japanese" in lang:
        return "ja"
    if "korean" in lang:
        return "ko"
    if "hindi" in lang:
        return "hi"
    if "bengali" in lang:
        return "bn"
    if "tamil" in lang:
        return "ta"
    if "urdu" in lang:
        return "ur"
    if "chinese" in lang:
        return "zh-CN"
    if "french" in lang:
        return "fr"
    if "german" in lang:
        return "de"

    session["language"] = "english"
    return "en"


@app.route("/level1", methods=["POST"])
def level1():
    print("level 1....\n\n\n")
    session["transcription"] = request.form["query"] if "query" in request.form else ""
    session["prompt_level1"] = (
        "" if "prompt_level1" not in session else session["prompt_level1"]
    )

    if request.form["leng"] != "":
        session["language"] = request.form["leng"]

    session["language"] = (
        "english" if session["language"] == "" else session["language"]
    )

    if request.form["fast"] == "true":
        session["toggle"] = "fast"
    if request.form["slow"] == "true":
        session["toggle"] = "slow"
    if request.form["groq"] == "true":
        session["toggle"] = "groq"

    audio_file = request.files["audio"] if "audio" in request.files else None

    try:
        if audio_file:
            audio_bytes = audio_file.read()
            audio_file = FileWithNames(audio_bytes)
            session["transcription"], session["language"] = transcribe(audio_file)
            session["language"] = get_language(session["language"])
            if session["language"].lower() != "en":
                session["transcription"] = translate_text(
                    session["transcription"], "en"
                )
    except Exception as e:
        session["language"] = "en"
        print(e)
        update_logs(e)
        session["transcription"] = "Error."
    return jsonify({"message": "Data received, start streaming"})


@app.route("/level1/stream")
def level1_stream():
    global p1, layer_1
    print(layer_1, "layer 1  dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    # Load the configuration to get className1
    data = readAndWriteJsonData("configu.json", "r")
    config_data = data.get("layer1", demo_configuration('layer1'))

    class_name1 = config_data["classNamelayer1"]
    print(class_name1, "class Name is given")
    # Capitalize the first letter of className1
    ClassName1 = class_name1.capitalize()
    print(ClassName1, "what is this mannnnnnnnn")

    try:
        context1 = ""
        metadata1 = []
        # Use class_name1 for ddbot300
        context1, metadata1 = qdb(
            session["transcription"],
            layer_1,
            class_name1,
            ClassName1,
            chunk_id=1,
            limit=2,
        )
        print(context1, class_name1, ClassName1, "the value is here should we take")
        # Assuming you also want to apply the same logic to ddbot100
        # Just replace "ddbot100" and "Ddbot100" with appropriate variables if needed
        context2, metadata2 = qdb(
            session["transcription"],
            layer_1,
            class_name1,
            ClassName1,
            chunk_id=3,
            limit=2,
        )
        context = context1 + context2
        metadata = metadata1 + metadata2
        sufficient = False
    except Exception as e:
        print("\n\n\nError:    ", e)
        update_logs(e)
        context = "No context"
        metadata = ["1"]

    try:
        resp = Response(
            ask_gpt(
                question=session["transcription"],
                context=context,
                gpt="gpt-4",
                language=session["language"],
                metadata=metadata,
                addition=p1,
                userid=session["userID"],
                filename="Layer_1_file/file_info_1.json",
            ),
            content_type="text/event-stream",
        )
        return resp
    except:
        data = {"response": "Error.", "sufficient": False}
        json_data = json.dumps(data)
        resp = "data: {json_data}\n\n"
        return Response(resp, content_type="text/event-stream")


@app.route("/level2", methods=["POST"])
def level2():
    session["layer_1_response"] = request.form["response"]
    session["transcription"] = request.form["query"]
    return jsonify({"message": "Data received, start streaming"})


@app.route("/level2/stream")
def level2_stream():
    print("\n\n\nLever 2....\n\n\n")
    config_data1 = load_configuration1()
    class_name2 = config_data1["classNamelayer2"]
    print(class_name2, "class Name is given")
    # Capitalize the first letter of className1
    ClassName2 = class_name2.capitalize()
    print(ClassName2, "what is this mannnnnnnnn")
    global p2, layer_2
    print(layer_2, "layer_2 is working...................................")
    try:
        context, metadata = qdb(
            session["transcription"],
            layer_2,
            class_name2,
            ClassName2,
            chunk_id=1,
            limit=5,
        )
        sufficient = False
    except Exception as e:
        update_logs(e)
        context = "No context"
        metadata = ["1"]

    session["response"] = session["layer_1_response"]

    try:
        resp = Response(
            ask_gpt(
                question=session["transcription"],
                context=context,
                gpt="gpt-4",
                language=session["language"],
                metadata=metadata,
                addition=p2,
                userid=session["userID"],
                filename="Layer_1_file/file_info_2.json",
            ),
            content_type="text/event-stream",
        )

        return resp
    except:
        data = {"response": "Error.", "sufficient": False}
        json_data = json.dumps(data)
        resp = "data: {json_data}\n\n"
        return Response(resp, content_type="text/event-stream")


def insert_data(table_name, data):
    table_id = f"my-project-41692-400512.jobbot.{table_name}"

    if not isinstance(data, list):
        data = [data]

    errors = dbclient.insert_rows_json(table_id, data)

    if errors == []:
        print(f"Data added successfully into {table_name}")
    else:
        print(f"Encountered errors while inserting into {table_name} : {errors}")


def delete_data(table_name, identifier_column, identifier_value):

    table_id = f"my-project-41692-400512.jobbot.{table_name}"

    sql_query = f"""
        DELETE FROM `{table_id}`
        WHERE `{identifier_column}` = '{identifier_value}'
    """

    query_job = dbclient.query(sql_query)  # Make an API request.
    query_job.result()  # Waits for the query to finish

    print(
        f"Rows deleted in {table_name} where {identifier_column} is {identifier_value}."
    )


@app.route("/add_question", methods=["POST"])
def add_question():
    data = request.json

    question_id = str(uuid.uuid4())
    question = data.get("question")
    optionA = data.get("optionA")
    optionB = data.get("optionB")
    optionC = data.get("optionC")
    optionD = data.get("optionD")

    dataset_name = "my-project-41692-400512.jobbot"
    table_name = "questions"
    table_id = f"{dataset_name}.{table_name}"

    query = """
        INSERT INTO `{0}` (questionID, question, optionA, optionB, optionC, optionD)
        VALUES (@question_id, @question, @optionA, @optionB, @optionC, @optionD)
    """.format(
        table_id
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("question_id", "STRING", question_id),
            bigquery.ScalarQueryParameter("question", "STRING", question),
            bigquery.ScalarQueryParameter("optionA", "STRING", optionA),
            bigquery.ScalarQueryParameter("optionB", "STRING", optionB),
            bigquery.ScalarQueryParameter("optionC", "STRING", optionC),
            bigquery.ScalarQueryParameter("optionD", "STRING", optionD),
        ]
    )

    try:
        query_job = dbclient.query(query, job_config=job_config)  # Make an API request
        return jsonify({"message": "Question added successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500


def get_question_by_name(question_name):
    # Ensure this matches your actual BigQuery table ID
    table_id = "my-project-41692-400512.jobbot.questions"

    # Construct the query using a safe parameterized approach
    query = """
    SELECT *
    FROM `{}`
    WHERE question = @question_name
    """.format(
        table_id
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("question_name", "STRING", question_name),
        ]
    )

    query_job = dbclient.query(query, job_config=job_config)

    # Fetch the first row from the RowIterator
    try:
        result = next(query_job.result())
    except StopIteration:
        return None

    # Convert the result into a dictionary
    question_details = {
        "questionID": result[0],
        "question": result[1],
        "optionA": result[2],
        "optionB": result[3],
        "optionC": result[4],
        "optionD": result[5],
    }

    return question_details


@app.route("/questions", methods=["GET", "DELETE"])
def get_questions():
    try:
        # Construct the query to retrieve questions from BigQuery table
        dataset_name = (
            "my-project-41692-400512.jobbot"  # Replace with your actual dataset ID
        )
        table_name = "questions"
        table_id = f"{dataset_name}.{table_name}"

        query = """
            SELECT questionID, question, optionA, optionB, optionC, optionD
            FROM `{0}`
        """.format(
            table_id
        )

        # Execute the query
        query_job = dbclient.query(query)

        # Fetch the results
        results = query_job.result()

        # Convert results to a list of dictionaries
        questions = []
        for row in results:
            questions.append(
                {
                    "questionID": row.questionID,
                    "question": row.question,
                    "optionA": row.optionA,
                    "optionB": row.optionB,
                    "optionC": row.optionC,
                    "optionD": row.optionD,
                }
            )

        # Return the list of questions as JSON response
        return jsonify(questions), 200

    except Exception as e:
        return jsonify({"message": f"Error: {e}"}), 500


@app.route("/users")
def users():
    # Ensure this matches your actual BigQuery table ID
    table_id = "my-project-41692-400512.jobbot.users"

    # Construct the query using a safe parameterized approach
    sql_query = """
    SELECT * 
    FROM `{}`
    """.format(
        table_id
    )

    query_job = dbclient.query(sql_query)  # Make an API request.
    results = query_job.result()
    # Convert the results to a list of dictionaries
    user_data = []
    for row in results:
        user_data.append(dict(row))

    return jsonify(user_data)


from google.api_core.exceptions import BadRequest


def update_user_is_answered(userID, retry_count=3):
    print(userID, "user updated")
    try:
        # Define the update query
        query = f"""
        UPDATE `my-project-41692-400512.jobbot.users`
        SET isAnswer = true
        WHERE userID = '{userID}'
        """

        # Execute the query
        query_job = dbclient.query(query)
        query_job.result()  # Wait for the query to complete
        print("user isAnswered updated")

    except BadRequest as e:
        # Handle specific error related to the streaming buffer
        if "streaming buffer" in str(e) and retry_count > 0:
            print(
                f"Streaming buffer issue encountered. Retrying... ({retry_count} attempts left)"
            )
            # Retry the operation after a short delay
            time.sleep(20)
            update_user_is_answered(userID, retry_count - 1)
        else:
            # Retry count exceeded or other error occurred
            print(f"An error occurred while updating user isAnswered: {str(e)}")


def update_answer(userID, answerID, answer):
    # Define the update query
    query = f"""
    UPDATE `my-project-41692-400512.jobbot.answers`
    SET answer = '{answer}'
    WHERE userID = '{userID}' AND answerID = '{answerID}'
    """

    # Execute the query
    query_job = dbclient.query(query)
    query_job.result()  # Wait for the query to complete
    print("Answer updated successfully")


import time


@app.route("/updateProfile", methods=["GET", "POST", "PUT"])
def create_profile():
    if request.method == "POST":
        # Handle POST request to create new data
        data = request.json
        userID = None

        if "userID" in session:
            userID = session["userID"]
        else:
            print("userID not found in session")

        # Update user's profile data
        for item in data:
            answerID = str(uuid.uuid4())
            question = item.get("question")
            answer = item.get("answer")
            fullQuestion = get_question_by_name(question)
            table_data = {
                "answerID": answerID,
                "questionID": fullQuestion["questionID"],
                "answer": answer,
                "userID": userID,
            }
            insert_data("answers", table_data)

        # Update user's isAnswered field to True in BigQuery
        update_user_is_answered(userID)

        return jsonify({"message": "Data received successfully"})

    elif request.method == "PUT":
        # Handle PUT request to update existing data
        data = request.json
        userID = None

        if "userID" in session:
            userID = session["userID"]
        else:
            print("userID not found in session")

        # Update user's profile data
        for item in data:
            answerID = item.get(
                "answerID"
            )  # Assuming answerID is provided in the request
            answer = item.get("answer")
            update_answer(userID, answerID, answer)

        return jsonify({"message": "Data updated successfully"})

    else:
        return render_template("profile.html")


@app.route("/audioInterval")
def audio_interval():
    def generate_audio():
        global audio_speech
        audio_speech = False
        if audio_speech:
            audio_file_path = "./output.mp3"
            audio_speech = None
            with open(audio_file_path, "rb") as audio_file:
                while True:
                    chunk = audio_file.read(1024)
                    if not chunk:
                        break
                    print("sending audio")
                    yield chunk
        else:
            print("No Audio")
            return {"error": "null"}

    return Response(generate_audio(), mimetype="audio/mpeg")


@app.route("/answers")
def get_user_answers():
    if "userID" not in session:
        return jsonify({"error": "User ID not found in session"}), 400

    # Get user ID from session
    userID = session["userID"]

    # Define the query to retrieve user's answers
    query = f"""
    SELECT answerID, answer, questionID
    FROM `my-project-41692-400512.jobbot.answers`
    WHERE userID = '{userID}'
    """

    # Execute the query
    query_job = dbclient.query(query)

    # Fetch all results
    results = query_job.result()

    # Prepare the response data
    answers = []
    for row in results:
        answer = {
            "answerID": row["answerID"],
            "answer": row["answer"],
            "question": get_question_text(
                row["questionID"]
            ),  # Assuming you have a function to get question text
        }
        answers.append(answer)

    # Return the answers as JSON response
    return jsonify({"answers": answers})


def get_question_text(questionID):
    # Define the query to retrieve the question text based on questionID
    query = f"""
    SELECT question
    FROM `my-project-41692-400512.jobbot.questions`
    WHERE questionID = '{questionID}'
    """

    # Execute the query
    query_job = dbclient.query(query)

    # Fetch all results
    results = query_job.result()

    # Extract the question text from the result
    for row in results:
        question_text = row["question"]
        return question_text

    return "Question not found"


CREDENTIALS_FILE = "drive.json"

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "drive.json"
DOWNLOAD_DIRECTORY = "download_files"
INFO_FILE_PATH = os.path.join(DOWNLOAD_DIRECTORY, "file_info.json")


@app.route("/new_panel")
def drive():
    return render_template("new_panel.html")


# Replace with your actual folder ID

########################################################

lm_client = None


layer_1 = None

global layer_2
layer_2 = None

global openai_flag
openai_flag = True

global layer_1_flag
layer_1_flag = True

global layer_2_flag
layer_2_flag = True

global error_admin_msg
error_admin_msg = "error."

@app.route('/loading_status')
def loading_status():
    global loading_status
    loading_status = {"status": loading_status}
    return jsonify(loading_status)


def demo_configuration(layer_name):
    # key
    layer_url_key = f"{layer_name}URL"
    layer_drive_url_key = f"{layer_name}DriveURL"
    layer_auth_key = f"{layer_name}AuthKey"
    layer_class_name_key = f"className{layer_name}"
    
    return {
        "openaiKey": "",
        layer_url_key: "",  
        layer_drive_url_key: "",  
        layer_auth_key: "",  
        layer_class_name_key: "",  
    }

def initiate_clients():
    global openai_flag, layer_1_flag, layer_2_flag, lm_client, layer_1, layer_2, error_admin_msg, loading_status
    # config_data = load_configuration()
    data = readAndWriteJsonData("configu.json", "r")
    config_data = data.get("layer1", demo_configuration('layer1'))
    config_data1 = data.get("layer2", demo_configuration('layer2'))

    print(config_data,'\n \n')

    print(config_data1,'\n \n')

    try:
        openai.api_key = config_data["openaiKey"]
        lm_client = openai.OpenAI(api_key=config_data["openaiKey"])
        msg = [
            {"role": "system", "content": "system_message"},
            {"role": "user", "content": "user_message"},
        ]

        response = lm_client.chat.completions.create(
            model="gpt-4",
            messages=msg,
            max_tokens=1000,
            temperature=0.0,
        )
        openai_flag = False
        loading_status = "LLM Client Working..."
        print("lm_client working")
    except:
        openai_flag = True
        print("lm_client not working")
        loading_status = "LLM Client not Working..."

    try:
        layer_1 = weaviate.Client(
            url=config_data["layer1URL"],
            auth_client_secret=weaviate.AuthApiKey(
                api_key=config_data["layer1AuthKey"]
            ),
            additional_headers={"X-OpenAI-Api-Key": config_data["openaiKey"]},
        )
        print("layer 1 working", layer_1)
        loading_status = "layer 1 working..."
        check_for_updates(config_data, "download_files", "file_info_1.json")
        layer_1_flag = False
    except:
        layer_1_flag = True

    try:
        layer_2 = weaviate.Client(
            url=config_data1["layer2URL"],
            auth_client_secret=weaviate.AuthApiKey(
                api_key=config_data1["layer2AuthKey"]
            ),
            additional_headers={"X-OpenAI-Api-Key": config_data["openaiKey"]},
        )
        layer_2_flag = False
        check_for_updates(config_data, "download_files_2", "file_info_2.json")
        loading_status = "layer 2 working..."
        print("layer 2 working")
    except:
        layer_2_flag = True

    loading_status = None
    error_admin_msg = ""
    if openai_flag:
        error_admin_msg += "Please check your OpenAI API KEY.\n"
    if layer_1_flag:
        error_admin_msg += "Please check your Layer_1 API KEY.\n"
    if layer_2_flag:
        error_admin_msg += "Please check your Layer_2 API KEY.\n"


initiate_clients()

def get_google_drive_service():
    from google.oauth2.credentials import Credentials

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("drive", "v3", credentials=creds)
    return service

def download_folder(folder_url, save_directory, json_file):
    global loading_status
    loading_status = "Drive Files downloading Started..."
    folder_id = folder_url.split("/")[-1]
    service = get_google_drive_service()

    query = f"'{folder_id}' in parents"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    file_info_list = []
    page_token = None

    try:
        while True:
            response = (
                service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            items = response.get("files", [])
            for item in items:
                file_id = item["id"]
                file_name = item["name"]
                modified_time = item["modifiedTime"]
                mimeType = item["mimeType"]
                file_path = os.path.join(save_directory, file_name)

                if mimeType.startswith("application/vnd.google-apps."):
                    continue

                drive_request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, drive_request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)

                with open(file_path, "wb") as f:
                    f.write(fh.read())
                    print(f"{file_name} has been downloaded.")
                    loading_status = f"{file_name} has been downloaded."

                file_info_list.append(
                    {"id": file_id, "name": file_name, "modifiedTime": modified_time}
                )

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        info_file_path = os.path.join(save_directory, json_file)
        with open(info_file_path, "w") as json_file:
            json.dump(file_info_list, json_file, indent=4)
            print("JSON file written successfully.")
            loading_status = "JSON file written successfully."

        return {
            "status": "success",
            "message": "Files downloaded successfully.",
            "files": file_info_list,
        }

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return {"status":"failure"}

@app.route("/check_for_updates")
def check_for_updates_route():
    layer = request.args.get("layer")

    if layer not in ["layer1", "layer2"]:
        return jsonify({"error": "Invalid layer specified. Please use 'layer1' or 'layer2'."}), 400
    
    # Load configuration once and use it throughout
    data = readAndWriteJsonData("configu.json", "r")
    if not data:  # If data is None or empty
        data = {}  # Ensure data is a dict to prevent further errors

    # Decide on directory and info_file_name based on layer
    if layer == "layer1":
        config = data.get("layer1", demo_configuration('layer1'))
        directory = "download_files"
        info_file_name = "file_info_1.json"
    else:  # For layer2
        config = data.get("layer2", demo_configuration('layer2'))
        directory = "download_files_2"
        info_file_name = "file_info_2.json"

    # Construct layer_config with proper fallbacks
    layer_config = {
        "driveURL": config.get(f"{layer}DriveURL", ""),
        "layerURL": config.get(f"{layer}URL", ""),
        "layerAuthKey": config.get(f"{layer}AuthKey", ""),
        "className": config.get(f"className{layer}", ""),
        "openaiKey": config.get("openaiKey", ""),
    }

    try:
        update_result = check_for_updates(layer_config, directory, info_file_name)
        if isinstance(update_result, dict) and update_result.get("status") == "success":
            print("\nUpdate recognized file changes!..\n")
            pdf_vectorization(directory, layer_config)
            print("Files got vectorized successfully.")
        else:
            return (
                jsonify(
                    {"error": "Failed to process files.", "details": update_result}
                ),
                500,
            )
    except Exception as e:
        app.logger.error(f"Error while processing files: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Delete files in the directory except for those starting with 'file_info'
        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                if not file_name.startswith("file_info"):
                    file_path = os.path.join(directory, file_name)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                        print(f"Deleted {file_name}")
                    except Exception as e:
                        app.logger.error(f"Failed to delete {file_name}. Reason: {e}")
            print("Non-essential files deleted after vectorization.")

    return jsonify({"message": "Files processed successfully."})


def check_for_updates(layer_config, directory, info_file_name):
    drive_url = layer_config["driveURL"]
    global loading_status
    loading_status = "Looking in Drive..."

    info_file_path = os.path.join(directory, info_file_name)

    service = get_google_drive_service()
    folder_id = drive_url.split("/")[-1]
    query = f"'{folder_id}' in parents"

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

        existing_files_info = []
        if os.path.exists(info_file_path):
            with open(info_file_path, "r") as file:
                existing_files_info = json.load(file)

        existing_files_ids = {file["id"]: file for file in existing_files_info}

        current_files_info = []
        page_token = None
        while True:
            response = (
                service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            items = response.get("files", [])
            for item in items:
                current_files_info.append(item)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        # Process new and updated files
        for item in current_files_info:
            process_file(service, item, directory, existing_files_ids)

        # Detect and handle deleted files
        detect_and_handle_deleted_files(
            existing_files_info, current_files_info, directory
        )

        # Update the file info JSON
        with open(info_file_path, "w") as json_file:
            json.dump(current_files_info, json_file, indent=4)
            loading_status = f"File info JSON updated for {directory}."
            print(f"File info JSON updated for {directory}.")

        return {"message": "Update check completed successfully", "status": "success"}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": str(e), "status": "error"}, 500


def process_file(service, item, directory, existing_files_ids):
    global loading_status
    loading_status = "Loading or Updating Starting..."

    file_id = item["id"]
    file_name = item["name"]
    mimeType = item["mimeType"]
    modified_time = item["modifiedTime"]
    file_path = os.path.join(directory, file_name)

    # Skip temporary or system files often created by Office applications
    if file_name.startswith("~$"):
        print(f"Skipping temporary or system file: {file_name}")
        return False, None

    file_is_new_or_updated = False

    if (
        file_id not in existing_files_ids
        or existing_files_ids[file_id].get("modifiedTime", "") != modified_time
    ):
        download_file(service, file_id, file_path, mimeType, file_name)
        print(f"Downloaded or updated file: {file_name}")
        file_is_new_or_updated = True

    return file_is_new_or_updated, file_path


def detect_and_handle_deleted_files(existing_files_info, current_files_info, directory):
    global loading_status
    current_files_ids = {file["id"] for file in current_files_info}
    print(f"Current files in Drive: {current_files_ids}")
    for existing_file in existing_files_info:
        if existing_file["id"] not in current_files_ids:
            file_path = os.path.join(directory, existing_file["name"])
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {existing_file['name']}")
                except Exception as e:
                    print(f"Error deleting file {existing_file['name']}: {e}")
            else:
                loading_status = f"File not found for deletion: {file_path}..."
                print(f"File not found for deletion: {file_path}")


def download_file(service, file_id, file_path, mimeType, file_name):
    try:
        # Determine if the file is a Google Docs type and needs exporting
        if mimeType.startswith("application/vnd.google-apps."):
            export_mime_type = "application/pdf"  # Default export MIME type
            file_extension = "pdf"
            if mimeType == "application/vnd.google-apps.document":
                export_mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                file_extension = "docx"
            elif mimeType == "application/vnd.google-apps.spreadsheet":
                export_mime_type = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                file_extension = "xlsx"
            elif mimeType == "application/vnd.google-apps.presentation":
                export_mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                file_extension = "pptx"

            # Adjust the file path to use the appropriate file extension
            file_path = f"{file_path.rsplit('.', 1)[0]}.{file_extension}"
            request = service.files().export_media(
                fileId=file_id, mimeType=export_mime_type
            )
        else:
            request = service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Write the file's contents to the specified local path
        with open(file_path, "wb") as f:
            f.write(fh.getvalue())
            print(f"Downloaded or exported file: {file_name} to {file_path}")

    except Exception as e:
        print(f"An error occurred while downloading/exporting '{file_name}': {e}")

def split_pdf_text_by_page(pdf_path):
    pages = []
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            pages.append(text)
    return pages


def load_documents(directory, glob_patterns):
    documents = []
    for glob_pattern in glob_patterns:
        file_paths = glob.glob(os.path.join(directory, glob_pattern))
        for fp in file_paths:
            try:
                if fp.endswith(".docx"):
                    text = docx2txt.process(fp)
                    pages = [text]  # Treat the whole document as a single "page"
                elif fp.endswith(".pdf"):
                    pages = split_pdf_text_by_page(fp)
                else:
                    print(f"Warning: Unsupported file format for {fp}")
                    continue
                documents.extend(
                    [
                        (page, os.path.basename(fp), i + 1)
                        for i, page in enumerate(pages)
                    ]
                )
            except Exception as e:
                print(f"Warning: The file {fp} could not be processed. Error: {e}")
    return documents


def split_text(text, file_name, chunk_size, chunk_overlap):
    start = 0
    end = chunk_size
    while start < len(text):
        yield (text[start:end], file_name)
        start += chunk_size - chunk_overlap
        end = start + chunk_size


def split_documents(documents, chunk_size, chunk_overlap):
    texts = []
    metadata = []
    for doc_text, file_name, page_number in documents:
        for chunk in split_text(doc_text, file_name, chunk_size, chunk_overlap):
            sentence = chunk[0]
            texts.append(sentence)
            metadata.append(str(file_name) + " Pg: " + str(page_number))

    return texts, metadata


def clear_directory(dir_path):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def convert_pdf2img(input_file, output_dir="eximages"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        clear_directory(output_dir)

    pdfIn = fitz.open(input_file)
    output_files = []
    for pg in range(pdfIn.page_count):
        page = pdfIn.load_page(pg)
        zoom_x = 2
        zoom_y = 2
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        output_file = os.path.join(
            output_dir,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_page_{pg+1}.png",
        )
        pix.save(output_file)
        output_files.append(output_file)
    pdfIn.close()
    return output_files
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_text_from_image(image_path, api_key, file_path):
    base64_image = encode_image(image_path)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "The image is from a PPT. Tradiotional text extraction does not preserve the structure. In that, I can still extract the text, but, it will be impossible to format it into correct headings and sections, and questions and asnwers, as it is not a tradtional document. I want you to return properly formatted text. Do not skip out on anything. Also, do not say 'here is what the image says..', etc. Directly start producing image transcription .I will be directly copying this into a document. people should nt know this has been generated by you. People reading it must be convinced and it should carry the same and complete information as in the image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        "max_tokens": 4000,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    if response.status_code == 200:
        response_data = response.json()
        text_response = (
            response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
    else:
        text_response = f"Error: {response.status_code}, Message: {response.text}"

    filename = image_path.replace("eximages", "")
    new_data = {filename: text_response}

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    data.update(new_data)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def process_all_pdfs(pdf_folder, api_key, file_path):
    global loading_status
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            convert_pdf2img(pdf_path)
            loading_status = f"Processed {filename}"
            print(f"\n\nProcessed {filename}\n\n")
            for image_filename in os.listdir("eximages"):
                image_path = os.path.join("eximages", image_filename)
                print(image_path)
                get_text_from_image(image_path, api_key, file_path)


def pdf_vectorization(directory, layer_config, processed_files=set(), chunk_size=400):
    global loading_status
    class_name = layer_config["className"]
    url = layer_config["layerURL"]
    auth_key = layer_config["layerAuthKey"]
    openai_key = layer_config["openaiKey"]
    print(class_name, "ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")

    client = weaviate.Client(
        url=url,
        auth_client_secret=weaviate.AuthApiKey(api_key=auth_key),
        additional_headers={"X-OpenAI-Api-Key": openai_key},
    )
    loading_status = "Vecotring Documents."
    print(client, "client is the value of i am getting")
    glob_patterns = ["*.docx", "*.pdf"]
    documents = load_documents(directory, glob_patterns)

    chunk_overlap = 0
    texts, metadata = split_documents(documents, chunk_size, chunk_overlap)

    data_objs = [{"text": tx, "metadata": met} for tx, met in zip(texts, metadata)]
    total = len(data_objs)

    i = 0

    class_obj = {
        "class": class_name,
        "properties": [
            {
                "name": "text",
                "dataType": ["text"],
            },
            {
                "name": "metadata",
                "dataType": ["text"],
            },
        ],
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {
                "vectorizeClassName": False,
                "model": "ada",
                "modelVersion": "002",
                "type": "text",
            },
        },
    }
    try:
        client.schema.create_class(class_obj)
    except Exception as e:
        print("Error:", e)
        print("--------*--------**")
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)

    client.batch.configure(batch_size=50)
    with client.batch as batch:
        for data_obj in data_objs:
            filename = os.path.basename(data_obj["metadata"])
            if filename not in processed_files:
                i += 1
                if i > -1:
                    loading_status = "Uploaded: "+ str(i)+ "/"+ str(total)

                    print(loading_status)
                    batch.add_data_object(data_obj, class_name)
                    processed_files.add(filename)  # Mark the file as processed
                else:
                    print("Already present.", i)

    res = (
        client.query.get(class_name, ["text", "metadata"])
        .with_near_text({"concepts": "What do I do with my life??"})
        .with_limit(10)
        .do()
    )
    print("\n\n", class_name, "\n\n")
    print(res)
    return processed_files

smart_function = [
    {
        "name": "return_response",
        "description": "to be used to return list of chunks.",
        "parameters": {
            "type": "object",
            "properties": {
                "item_list": {
                    "type": "array",
                    "description": "List of chunks directly extracted from the document given",
                    "items": {"type": "integer"},
                },
            },
            "required": ["item_list"],
        },
    }
]

def ask_gpt_smart_chunk(question):
    system_message = "You are a smart chunker. You will be given content from a slide/document page. You need to return the data, but divided into chunks - meaning, the chunk you return must encapsulate complete information about somthing. You are allowed to return as many chunks as you like. But, you must cover the entire information. The reasons is that I will be feeding this into a vector database for semantic retrival of vectors. By feeding an entire page, the similarity scores are very low for specific queries that are only a fraction of the larger page. But, if I were to auto chunk it by 100 or some words, then there are cases where information could be cut off, etc, Therefore, you must return a list of strings. This is called smart chunking. Finally, remeber, what you return, when read, must preserve context. Just returning names, or sentences without any indication of the context or what they represent will be useless."
    user_message = "content from page from document below: \n" + question
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    print("-----------------------")
    response = lm_client.chat.completions.create(
        model="gpt-4",
        messages=msg,
        max_tokens=500,
        temperature=0.0,
        functions=smart_function,
        function_call="auto",
    )
    reply = response.choices[0].message.content
    try:
        reply = ast.literal_eval(reply)
    except:
        try:
            reply = json.loads(response.choices[0].message.function_call.arguments)[
                "item_list"
            ]
            print(reply)
        except:
            print(reply)
            reply = []

    return reply


def smart_chunk(exisiting_json, processed_json_name):
    with open(exisiting_json, "r") as file:
        data = json.load(file)
    new_data = {}

    for key, value in data.items():
        print(key)
        chunk_id = 0
        check = key + " " + str(chunk_id)
        try:
            with open(processed_json_name, "r") as file:
                data = json.load(file)
            if check in data:
                print("Moving on..")
                continue
        except Exception as e:
            print(e)
            data = None
        processed_list = ask_gpt_smart_chunk(value)
        for item in processed_list:
            new_data[key + " " + str(chunk_id)] = item
            if data is not None:
                data.update(new_data)
                new_data = data
            chunk_id += 1
            with open(processed_json_name, "w") as new_file:
                json.dump(new_data, new_file, indent=4)


def json_vectorize(json_file, layer_config):
    global loading_status
    class_name = layer_config["className"]
    url = layer_config["layerURL"]
    auth_key = layer_config["layerAuthKey"]
    openai_key = layer_config["openaiKey"]

    client = weaviate.Client(
        url=url,
        auth_client_secret=weaviate.AuthApiKey(api_key=auth_key),
        additional_headers={"X-OpenAI-Api-Key": openai_key},
    )

    with open(json_file, "r") as file:
        data = json.load(file)

    data_objs = []
    data_objs = [{"text": value, "metadata": key} for key, value in data.items()]
    total = len(data_objs)
    class_obj = {
        "class": class_name,
        "properties": [
            {
                "name": "text",
                "dataType": ["text"],
            },
            {
                "name": "metadata",
                "dataType": ["text"],
            },
        ],
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {
                "vectorizeClassName": False,
                "model": "ada",
                "modelVersion": "002",
                "type": "text",
            },
        },
    }

    try:
        client.schema.create_class(class_obj)
    except:
        print("exists")
    print("--------*--------**")
    i = 0
    client.batch.configure(batch_size=100)
    with client.batch as batch:
        for data_obj in data_objs:
            i += 1
            if i > -1:
                loading_status = "Uploaded: "+ str(i)+ "/"+ str(total)
                print(loading_status)
                batch.add_data_object(data_obj, class_name)
            else:
                print(i)

    res = (
        client.query.get(class_name, ["text", "metadata"])
        .with_near_text({"concepts": "What do I do with my life??"})
        .with_limit(10)
        .do()
    )
    print(res)

def delete_files(directory):
    if os.path.exists(directory):
            for file_name in os.listdir(directory):
                if not file_name.startswith('file_info'):
                    file_path = os.path.join(directory, file_name)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                        print(f"Deleted {file_name}")
                    except Exception as e:
                        app.logger.error(f"Failed to delete {file_name}. Reason: {e}")
            print("Non-essential files deleted after vectorization.")

###########################################################################################################################
from datetime import datetime

def create_blank_json_with_timestamp(filename):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    name, extension = filename.rsplit('.', 1)
    filename_with_timestamp = f"{name}_{timestamp}.{extension}"
    
    with open(filename_with_timestamp, 'w') as file:
        json.dump({}, file)
    
    return filename_with_timestamp

@app.route("/update_files", methods=["POST"])
def update_files():
    global loading_status

    data = request.form
    layer = request.args.get("layer")

    loading_status = "Update Process started..."

    if layer == "layer1":
        update_layer(data, "layer1")
    elif layer == "layer2":
        update_layer(data, "layer2")

    return render_template("chat.html")


def update_layer(data, layer_name):
    global loading_status
    checkbox_status = data.get("myCheckbox", "off")
    slider_value_key = f"{layer_name.lower()}Slider"
    slider_value = data.get(slider_value_key, "0")
    process_image = True if checkbox_status == "on" else False

    layer_url_key = f"{layer_name}URL"
    layer_drive_url_key = f"{layer_name}DriveURL"
    layer_auth_key = f"{layer_name}AuthKey"
    layer_class_name_key = f"className{layer_name}"

    list_of_params = [layer_url_key, layer_drive_url_key, layer_auth_key, layer_class_name_key]
    for key in list_of_params:
        if key not in data or not data[key]:
            return jsonify({"error": "Missing values"}), 500

    layer_url = data.get(layer_url_key, "")
    layer_drive_url = data.get(layer_drive_url_key, "")
    layer_auth = data.get(layer_auth_key, "")
    layer_class_name = data.get(layer_class_name_key, "")
    openaiKey = data["openaiKey"]

    new_data = {
        "openaiKey": openaiKey,
        layer_url_key: layer_url,
        layer_drive_url_key: layer_drive_url,
        layer_auth_key: layer_auth,
        layer_class_name_key: layer_class_name,
        "process_image": process_image,
        f"{layer_name}SliderValue": int(slider_value),
    }

    existing_data = readAndWriteJsonData("configu.json", "r")

    if existing_data:
        existing_data[layer_name] = new_data
    else:
        existing_data = {layer_name: new_data}

    readAndWriteJsonData("configu.json", "w", existing_data)


    download_directory = ""

    if layer_name == "layer1":
         download_directory='Layer_1_file'
    elif layer_name == "layer2":
        download_directory='Layer_2_file'


    response_data = download_folder(
            layer_drive_url, save_directory=download_directory, json_file="file_info_1.json"
        )
    
    if response_data.get("status") != "success":
            return jsonify({"error": "Failed to download files"}), 500



    layer_config = {
        "className": layer_class_name,
        "layerURL": layer_url,
        "layerAuthKey": layer_auth,
        "openaiKey": openaiKey,
        "folderURL": layer_drive_url,
    }

    if process_image == True:
        img2txt_file = "image2txt.json"
        smart_chunk_json = "smart_chunk.json"
        img2txt_file = create_blank_json_with_timestamp(img2txt_file)
        smart_chunk_json = create_blank_json_with_timestamp(smart_chunk_json)
        loading_status = "processing files."
        process_all_pdfs(download_directory, openaiKey, img2txt_file)
        loading_status = "Smart chunking...."
        smart_chunk(img2txt_file, smart_chunk_json)
        json_vectorize(smart_chunk_json, layer_config)
    else:
        pdf_vectorization(download_directory, layer_config, set(), int(slider_value))

    initiate_clients()
    print("Files downloaded and vectorized.")
    loading_status = "Files downloaded and vectorized."
    delete_files(download_directory)
    return jsonify({"success": "Done"}), 500



@app.route("/admin_list", methods=["GET", "POST", "PATCH", "DELETE"])
def admin_list():
    try:
        if request.method == "GET":
            return render_template("admin.html")

        elif request.method == "PATCH":
            # Parse request data
            data = request.json
            user_id = data.get("userId")
            role = data.get("role")

            # Update user's admin status in BigQuery
            update_admin_status(user_id, role)

            return jsonify({"message": "Admin status updated successfully"})

        elif request.method == "DELETE":
            # Parse request data
            user_id = request.args.get("userId")
            # Delete user from BigQuery
            status = delete_user(user_id)
            if status:
                return jsonify({"message": "User deleted successfully"})
            else:
                return jsonify(
                    {"message": "User deleted successfully", "status": status}
                )
    except Exception as e:
        # Handle any exceptions that occur during the execution of the route
        return jsonify({"error": str(e)})


def update_admin_status(user_id, role):
    try:
        # Initialize BigQuery client
        table_id = "my-project-41692-400512.jobbot.users"
        # Define the update query
        update_query = f"""
            UPDATE `{table_id}`
            SET role = '{role}'
            WHERE userID = '{user_id}'
        """

        # Build the job configuration
        job_config = bigquery.QueryJobConfig()

        # Run the update query
        query_job = dbclient.query(update_query, job_config=job_config)

        # Wait for the query to complete
        query_job.result()

        print(f"Role updated to admin for user ID: {user_id}")

    except Exception as e:
        print(f"Error updating admin status for user ID {user_id}: {e}")


def delete_user(user_id):
    try:
        # Define the BigQuery table ID
        table_id = "my-project-41692-400512.jobbot.users"

        # Define the delete query
        query = f"""
        DELETE FROM `{table_id}`
        WHERE userID = '{user_id}'
        """

        # Execute the delete query
        query_job = dbclient.query(query)
        query_job.result()  # Wait for the query to complete

        print(f"User with userID {user_id} deleted successfully")

    except Exception as e:
        print(f"Error deleting user with user ID {user_id}: {e}")


@app.route("/whiteList", methods=["POST"])
def update_user_WhiteList():
    try:
        dataset_name = "my-project-41692-400512.jobbot.users"
        table_id = f"{dataset_name}"

        data = request.json
        email = data["email"]
        isWhitelist = data["isWhiteList"]

        is_white_list_str = "true" if isWhitelist else "false"

        query = f"""
            UPDATE `{table_id}`
            SET iswhiteList = {is_white_list_str}
            WHERE email = @email
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
        )

        query_job = dbclient.query(query, job_config=job_config)
        query_job.result()

        return {"message": "User WhiteList updated successfully"}

    except Exception as e:
        return {"message": f"Error updating user WhiteList: {str(e)}"}

def makeThemWhiteList():
    try:
        table_id = "my-project-41692-400512.jobbot.users"

        query = f"""
            UPDATE `{table_id}`
            SET iswhiteList = FALSE
            WHERE role = 'admin'
        """

        job_config = bigquery.QueryJobConfig()

        query_job = dbclient.query(query, job_config=job_config)
        results = query_job.result()
        print("Update successful")
    except Exception as e:
        print(f"Error updating user whitelist: {str(e)}")

@app.route("/whiteListUsers")
def WhiteListUsers():
    table_id = "my-project-41692-400512.jobbot.users"

    sql_query = """
    SELECT * 
    FROM `{}`
    WHERE iswhiteList = TRUE
    """.format(
        table_id
    )

    query_job = dbclient.query(sql_query)
    results = query_job.result()

    user_data = []
    for row in results:
        user_data.append(dict(row))

    return jsonify(user_data)

if __name__ == "__main__":
    app.run(debug=True)