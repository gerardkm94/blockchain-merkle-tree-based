from flask import Flask
from blocklibs.chain.models import api

app = Flask(__name__)
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int("8300"))

    # serve(app,  host='0.0.0.0', port=5000)
