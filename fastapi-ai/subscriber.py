import zmq, threading


def start_subscriber_thread(port, cam_id, callback):

    def run():
        ctx = zmq.Context()
        socket = ctx.socket(zmq.SUB)
        socket.connect(f"tcp://127.0.0.1:{port}")
        socket.subscribe("")
        print(f"[SUB] Connected → cam={cam_id}, port={port}")

        while True:
            try:
                event = socket.recv_json()
                callback(cam_id, event)
            except Exception as e:
                print(f"[SUB] Error({cam_id}):", e)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
