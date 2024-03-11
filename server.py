from onpoint_app import app
from onpoint_app.controllers import costumers
from onpoint_app.controllers import jobs
from onpoint_app.controllers import providers
from onpoint_app.controllers import env


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=8000)