import zmq.asyncio, cv2, numpy as np, asyncio, msgpack


async def camera_frame_sub(tracks, ports):

    ctx = zmq.asyncio.Context()
    sub = ctx.socket(zmq.SUB)

    sub.setsockopt(zmq.LINGER, 0)
    sub.setsockopt(zmq.RCVHWM, 2)
    sub.setsockopt(zmq.CONFLATE, 1)

    for port in ports:
        sub.connect(f"tcp://localhost:{port}")
    sub.setsockopt_string(zmq.SUBSCRIBE, "")

    try:
        while True:
            data = await sub.recv()
            msg = msgpack.unpackb(data, raw=False)

            cam_id = msg["cam_id"]
            jpg = msg["jpeg"]
            np_arr = np.frombuffer(jpg, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            for track in list(tracks):
                try:
                    await asyncio.wait_for(track.push(frame), timeout=0.1)
                except asyncio.TimeoutError:
                    pass
                except Exception as e:
                    print(f"[SUBSCRIBER] Error pushing to track: {e}")

    except asyncio.CancelledError:
        print("[SUBSCRIBER] Task cancelled")
        raise
    except Exception as e:
        print(f"[SUBSCRIBER] Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        sub.close()
        ctx.term()
        print("[SUBSCRIBER] Cleaned up")
