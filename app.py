from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Trasa z parametrem
@app.route('/about')         # Strona /about
def about():
    return "O nas"

@app.route('/login')         # Strona /about
def do_start():
    return "ekran logowania"

@app.route('/user/<name>')   # Parametr w URL
def user_profile(name):
    return f"Profil użytkownika: {name}"


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return "Formularz został wysłany!"
    else:
        return "Wyświetl formularz kontaktowy"

# Uruchamianie aplikacji
if __name__ == '__main__':
    app.run(debug=True)