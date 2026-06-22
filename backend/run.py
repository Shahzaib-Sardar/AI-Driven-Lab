import logging
from app import create_app, socketio

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')

app = create_app()


if __name__ == "__main__":
    # Use SocketIO server to support realtime events (eventlet recommended)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
