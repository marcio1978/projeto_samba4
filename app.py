from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

def save_data_to_file(username, password, full_name, given_name, surname, email):
    data_line = f"{username},{password},{full_name},{given_name},{surname},{email}"
    
    with open('/home/marcio/projeto/usuarios', 'a') as file:
        file.write(f"{data_line}\n")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        given_name = request.form['given_name']
        surname = request.form['surname']
        email = request.form['email']
        
        save_data_to_file(username, password, full_name, given_name, surname, email)
        
        return redirect(url_for('success'))
    
    return render_template('register.html')

@app.route('/success')
def success():
    return "Usuário registrado com sucesso!"

if __name__ == '__main__':
    app.run(debug=True)


