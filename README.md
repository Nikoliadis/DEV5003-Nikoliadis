In order to run the script

1. python -m venv venv
2. venv\Scripts\activate
We Will Need To Deactivate Protection
  1. Open PowerShell (as Administrator).
    Run: powershell
    Type: Get-ExecutionPolicy
    And Then Type: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
3. pip install flask
4. pip install flask_sqlalchemy
5. pip install flask_login
6. pip install flask_migrate
7. Finally We Run "python server.py" to run the site!


Admin User Credentials

Username: Admin
Email: admin@gmail.com
Password Admin123!