import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from pdfminer.high_level import extract_text
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def extract_structured_data(text):
    
    structured_data = {
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "linkedin": None,
        "peerlist": None,
        "work_experience": [],
        "education": [],
        "skills": [],
        "achievements": []
    }

    #  Email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        structured_data["email"] = email_match.group()

    #  Phone Number 
    phone_match = re.search(r"\b\d{10}\b", text)
    if phone_match:
        structured_data["phone"] = phone_match.group()

    # LinkedIn Profile
    linkedin_match = re.search(r"(https?:\/\/(www\.)?linkedin\.com\/[^\s]+)", text)
    if linkedin_match:
        structured_data["linkedin"] = linkedin_match.group()

    # Peerlist Profile
    peerlist_match = re.search(r"(https?:\/\/(www\.)?peerlist\.io\/[^\s]+)", text)
    if peerlist_match:
        structured_data["peerlist"] = peerlist_match.group()

    # Name 
    words = text.strip().split()
    if len(words) >= 2:
        structured_data["first_name"] = words[0].strip()
        structured_data["last_name"] = words[1].strip()

    # Education
    education_keywords = ["education", "academic", "qualification", "degree", "bachelor", "master", "B.Tech", "M.Tech", "PhD"]
    structured_data["education"] = [
        line.strip() for line in text.split("\n") if any(keyword in line.lower() for keyword in education_keywords)
    ]




    #  Work Experience
    experience_keywords = ["experience", "work", "internship", "job", "position", "company"]
    structured_data["work_experience"] = [
        line.strip() for line in text.split("\n") if any(keyword in line.lower() for keyword in experience_keywords)
    ]

    # Skills 


    skills_match = re.search(r"skills[:\s]*([\s\S]+?)(\n\n|\n[A-Z])", text, re.IGNORECASE)
    if skills_match:
        skills_text = skills_match.group(1).strip()
        structured_data["skills"] = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
    # Achievements
    achievement_keywords = ["award", "honor", "achievement", "certification", "recognition"]
    structured_data["achievements"] = [
        line.strip() for line in text.split("\n") if any(keyword in line.lower() for keyword in achievement_keywords)
    ]

    return structured_data

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)


    extracted_text = extract_text(file_path)
    
    
    structured_data = extract_structured_data(extracted_text)

    return jsonify({"message": "File processed successfully", "data": structured_data})

if __name__ == "__main__":
    app.run(debug=True)
