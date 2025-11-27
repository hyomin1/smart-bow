import zmq.asyncio, cv2, numpy as np, asyncio, msgpack, logging

logger = logging.getLogger(__name__)


async def camera_frame_sub(tracks, ports):

    ctx = zmq.asyncio.Context()
    sub = ctx.socket(zmq.SUB)

    sub.setsockopt(zmq.LINGER, 0)
    sub.setsockopt(zmq.RCVHWM, 2)
    sub.setsockopt(zmq.CONFLATE, 1)

    for port in ports:
        sub.connect(f"tcp://localhost:{port}")
        logger.info(f"ZMQ 구독 연결: {port}")
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
                    logger.error(f"트랙 push 실패: {e}", exc_info=True)

    except asyncio.CancelledError:
        logger.info("ZMQ 구독 작업 취소됨")
        raise
    except Exception as e:
        logger.error(f"ZMQ 구독 오류: {e}", exc_info=True)
        import traceback

        traceback.print_exc()
    finally:
        sub.close()
        ctx.term()
        logger.info("ZMQ 구독 정리 완료")
