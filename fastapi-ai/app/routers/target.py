from fastapi import APIRouter, Query
from app.services.target_service import TargetService
from app.utils.transform import get_perspective_transform, transform_points
from app.frame_manager import frame_queue

import time


router = APIRouter()
target_service = TargetService()

@router.get("/target-corners")
def target_corners(tw: int = Query(...), th: int = Query(...)):
    frame = None
    src_pts = None

  
    for _ in range(50):
        if not frame_queue.empty():
            frame = frame_queue.get()
            src_pts = target_service.get_target_raw(frame)

            if src_pts:
              
                M, dst_pts = get_perspective_transform(src_pts, tw, th)
                corners = transform_points(src_pts, M)
                return {"corners": corners}

        time.sleep(0.1)  

  
    return {"corners": []}


