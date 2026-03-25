from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
        <body style="text-align: center; padding-top: 50px;">
            <h1>Hello! Flask App is Running! 🚀</h1>
            <p>Deployed with GitHub Actions</p>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'OK'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
