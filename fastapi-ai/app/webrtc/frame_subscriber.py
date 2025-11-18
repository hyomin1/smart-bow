import zmq.asyncio, cv2, numpy as np, asyncio


async def camera_frame_sub(tracks, ports):

    ctx = zmq.asyncio.Context()
    sub = ctx.socket(zmq.SUB)

    sub.setsockopt(zmq.LINGER, 0)
    sub.setsockopt(zmq.RCVHWM, 1)

    for port in ports:
        sub.connect(f"tcp://localhost:{port}")
    sub.setsockopt_string(zmq.SUBSCRIBE, "")

    try:
        while True:
            cam_id, jpg = await sub.recv_multipart()

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
