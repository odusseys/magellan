from magellan.app import get_app


application = get_app()

if __name__ == "__main__":
    application.run(threaded=True, debug=True)
