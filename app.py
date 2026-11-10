from flask import Flask, request, render_template_string, jsonify
import json
import os

app = Flask(__name__)
DATA_PATH = "data/users.json"
REPORT_PATH = "data/reports.json"

def init_file():
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

init_file()

def read_user():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_report():
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_report(data):
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 简易AI故障识别
def ai_analyse(text):
    if "灯" in text or "照明" in text:
        return "照明故障"
    elif "水管" in text or "漏水" in text or "水龙头" in text:
        return "给排水故障"
    elif "空调" in text or "风扇" in text:
        return "电器故障"
    else:
        return "其他故障"

HTML_INDEX = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AI宿舍报修系统</title>
</head>
<body>
<h2>AI宿舍报修系统</h2>
<div>
<a href=" ">注册</a > | <a href="/login">登录</a >
</div>
</body>
</html>
"""

HTML_REG = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<h3>用户注册</h3>
<form method="post">
账号：<input type="text" name="username" required><br>
密码：<input type="password" name="pwd" required><br>
角色：
<select name="role">
<option value="student">学生</option>
<option value="repair">宿管维修</option>
<option value="admin">管理员</option>
</select>
<br>
<input type="submit" value="注册">
</form>
{{msg}}
</body>
</html>
"""

HTML_LOGIN = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<h3>登录</h3>
<form method="post">
账号：<input type="text" name="username" required><br>
密码：<input type="password" name="pwd" required><br>
<input type="submit" value="登录">
</form>
{{msg}}
</body>
</html>
"""

HTML_STUDENT = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<h3>学生报修页面</h3>
<form method="post">
宿舍号：<input type="text" name="room" required><br>
故障描述：<textarea name="desc" required></textarea><br>
<input type="submit" value="提交报修">
</form>
{{msg}}
<h4>我的报修记录</h4>
{{list}}
</body>
</html>
"""

HTML_REPAIR = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<h3>维修人员页面</h3>
{{list}}
</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<h3>管理员页面</h3>
{{list}}
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_INDEX)

@app.route("/register", methods=["GET","POST"])
def reg():
    msg=""
    if request.method=="POST":
        uname=request.form["username"]
        pwd=request.form["pwd"]
        role=request.form["role"]
        users=read_user()
        for u in users:
            if u["username"]==uname:
                msg="账号已存在"
                return render_template_string(HTML_REG,msg=msg)
        users.append({"username":uname,"pwd":pwd,"role":role})
        save_user(users)
        msg="注册成功，请登录"
    return render_template_string(HTML_REG,msg=msg)

@app.route("/login",methods=["GET","POST"])
def login():
    msg=""
    if request.method=="POST":
        uname=request.form["username"]
        pwd=request.form["pwd"]
        users=read_user()
        for u in users:
            if u["username"]==uname and u["pwd"]==pwd:
                if u["role"]=="student":
                    return student_page(uname)
                elif u["role"]=="repair":
                    return repair_page()
                elif u["role"]=="admin":
                    return admin_page()
        msg="账号密码错误"
    return render_template_string(HTML_LOGIN,msg=msg)

def student_page(name):
    if request.method=="POST":
        room=request.form["room"]
        desc=request.form["desc"]
        type_t=ai_analyse(desc)
        reports=read_report()
        reports.append({"room":room,"desc":desc,"type":type_t,"status":"待处理","owner":name})
        save_report(reports)
    reports=read_report()
    s_list=""
    for r in reports:
        if r["owner"]==name:
            s_list += f"宿舍{r['room']}，故障：{r['desc']}，AI分类：{r['type']}，状态：{r['status']}<br>"
    return render_template_string(HTML_STUDENT,msg="提交成功",list=s_list)

def repair_page():
    reports=read_report()
    s_list=""
    for idx,r in enumerate(reports):
        s_list += f"序号{idx+1}｜宿舍{r['room']}｜故障{r['desc']}｜AI分类{r['type']}｜状态{r['status']}<br>"
    return render_template_string(HTML_REPAIR,list=s_list)

def admin_page():
    reports=read_report()
    s_list=""
    for idx,r in enumerate(reports):
        s_list += f"序号{idx+1}｜宿舍{r['room']}｜故障{r['desc']}｜AI分类{r['type']}｜状态{r['status']}<br>"
    return render_template_string(HTML_ADMIN,list=s_list)

if __name__=="__main__":
    app.run(debug=True)