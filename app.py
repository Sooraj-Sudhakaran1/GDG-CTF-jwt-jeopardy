import datetime
import jwt
from flask import Flask, jsonify, make_response, render_template, request
app = Flask(__name__)
SECRET = "globex2024"
FLAG = "GDG{jwt_s3cr3t_crack1ng_ftw}"
def make_token(role: str = "employee") -> str:
    payload = {
        "user": "intern.sam",
        "role": role,
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")
@app.route("/") 
def home(): 
    return render_template("home.html") @app.route("/jwtchallenge") 
    def index(): token = make_token("employee") resp = make_response(render_template("index.html", token=token)) resp.set_cookie("token", token) 
    return resp
@app.route("/admin")
def admin():
    token = request.cookies.get("token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[len("Bearer "):]
    if not token:
        return jsonify({"error": "no token provided"}), 401
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError as exc:
        return jsonify({"error": f"invalid token: {exc}"}), 403
    if payload.get("role") != "admin":
        return jsonify({"error": "forbidden: admin role required",
                         "your_role": payload.get("role")}), 403
    return jsonify({"message": "Welcome, admin.", "flag": FLAG})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
