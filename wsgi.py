#from __init__ import init_app
from waitress import serve


from __init__ import app
#app,mail=init_app()

if __name__ == "__main__":
    app.run(debug=True)

