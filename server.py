from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session, render_template
import pyodbc
import jwt
secret_key = 'AndrewFuckingGurskiy'

app = Flask(__name__, static_folder='static')
app.secret_key = secret_key


# Строка подключения к базе данных SQL Server
conn_str = f'DRIVER={{SQL Server}};SERVER={{DIMASIK}};DATABASE={{cleaning}};TrustServerCertificate=yes;'
conn = pyodbc.connect(conn_str)



def generate_token(**kwargs):
    login = kwargs.get('login')
    client_id = kwargs.get('client_id')
    name = kwargs.get('name')
    email = kwargs.get('email')
    phone = kwargs.get('phone')
    address = kwargs.get('address')
    admin = kwargs.get('isAdmin')
    payload = {'login': login, 'client_id': client_id, 'name': name, 'email': email, 'phone': phone, 'address': address,
               'isUseful': True, 'isAdmin': admin}
    jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
    return jwt_token


@app.route('/login', methods=['POST'])
def login_form():
    try:
        data = request.json
        print(data)
        login = data['login']
        password = data['password']
        #operation = data['operation']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM CLIENTS WHERE login = ? and password = ?', login, password)
        rows = cursor.fetchone()
        cursor.close()
        print(rows)
        if rows:
            client_id = rows[0]
            name = rows[1]
            email = rows[4]
            phone = rows[5]
            address = rows[6]
            admin = rows[9]

            jwt_token = generate_token(login=login, client_id=client_id, name=name, email=email, phone=phone,
                                       address=address, isAdmin=admin)
            session['token'] = jwt_token
            return redirect(url_for('user_account', code=302))
        #elif (rows == None and operation == False)
           # cursor = conn.cursor()
            #cursor.execute()
        else:
            return jsonify({'auth': 'failed'})
    except pyodbc.Error as e:
        print('Error connecting to MS SQL Server:', e)
        return jsonify({'error': 'Error connecting to the database'})


@app.route('/')
def start_route():
    if 'token' not in session:
        # Если пользователь не авторизован, перенаправьте его на страницу аутентификации
        return send_from_directory('static', 'auth.html')
    else:
        # Если пользователь авторизован, отобразите содержимое личного кабинета
        return send_from_directory('static', 'user_account.html')


@app.route('/user_account', methods=['GET'])
def user_account():
    token = session.get('token')  # Получение токена из параметров запроса
    if token:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        if decoded_token['isUseful']:  # login = decoded_token['login']
            return send_from_directory(app.static_folder, 'user_account.html')
        else:
            return redirect('/'), 302
    else:
        return redirect('/'), 302


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/'), 302


@app.route('/user_data', methods=['GET'])
def user_info():
    token = session['token']
    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
    name = decoded_token['name']
    email = decoded_token['email']
    login = decoded_token['login']
    name = decoded_token['name']
    address = decoded_token['address']
    admin = decoded_token['isAdmin']
    phone = decoded_token['phone']
    return jsonify({'name': name, 'email': email, 'login': login, 'address': address, 'admin': admin, 'phone': phone})

@app.route('/before-current-table', methods=['POST'])
def your_endpoint():
    button_id = request.json.get('buttonId')
    # Здесь можете выполнить какую-то обработку, если необходимо
    return redirect(url_for('current_table', buttonId=button_id))

@app.route('/current-table', methods=['GET'])
def current_table():
    print('запрос получен')
    token = session['token']
    decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
    user_information = decoded_token['isAdmin']
    try:
        cursor = conn.cursor()
        button_id = request.args.get('buttonId')
        cursor.execute(f'SELECT * FROM {button_id}')
        rows = cursor.fetchall()
        # Получаем описание столбцов
        cursor.execute(f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?', button_id)
        columns_info = cursor.fetchall()
        cursor.close()
        print(columns_info)
        # Формируем список заголовков таблицы
        headers = [column[0] for column in columns_info]
        # Формируем данные для каждой строки таблицы
        data = []
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[headers[idx]] = value
            data.append(row_dict)
        print(headers, data)
        return render_template('currentTable.html', headers=headers, data=data, user_information=user_information)
    except Exception as e:
        print('запрос получен с ошибкой')
        error_message = f'Ошибка при выполнении запроса к базе данных: {str(e)}'
        return jsonify({'error': error_message}), 500


@app.route('/delete-data', methods=['POST'])
def delete_data():
    try:
        cursor = conn.cursor()
        query = request.json.get('query')  # Получаем ID пользователя из запроса
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        return jsonify({'query-failed': 'Данные успешно удалены'})
    except Exception as e:
        print("Ошибка удаления данных:", str(e))
        return jsonify({'query-failed': str(e)})  # Возвращаем ошибку сервера в случае исключения
    

@app.route('/update-data', methods=['POST'])
def update_data():
    try:
        cursor = conn.cursor()
        query = request.json.get('query')  # Получаем ID пользователя из запроса
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        return jsonify({'query-failed': 'Данные успешно обновлены'})
    except Exception as e:
        print("Ошибка обновления данных:", str(e))
        return jsonify({'query-failed': str(e)})  # Возвращаем ошибку сервера в случае исключения
    

@app.route('/new-data', methods=['POST'])
def new_data():
    try:
        cursor = conn.cursor()
        query = request.json.get('query')  # Получаем ID пользователя из запроса
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        return jsonify({'query-failed': 'Данные успешно добавлены'})
    except Exception as e:
        print("Ошибка добавления даных:", str(e))
        return jsonify({'query-failed': str(e)})  # Возвращаем ошибку сервера в случае исключения


if __name__ == '__main__':
    app.run(debug=True)

