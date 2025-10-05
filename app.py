from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')         # Strona /about
def do_start():
    return render_template('logowanie.html')

@app.route('/login', methods=['GET', 'POST'])
def do_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Przykładowy warunek – zamień na własny system autoryzacji!
        if email == 'twojbesciakwokolicy@best.pw.edu.pl' and password == 'haslo123':
            return redirect(url_for('dashboard'))
        else:
            error = 'Nieprawidłowy email lub hasło!'
    return render_template('logowanie.html', error=error)

@app.route('/dashboard')
def dashboard():
    return "Witaj w swoim dashboardzie!"

# Uruchamianie aplikacji
if __name__ == '__main__':
    app.run(debug=True)