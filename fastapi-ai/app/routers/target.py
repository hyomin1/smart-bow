from fastapi import APIRouter, Query, HTTPException
from app.services.target_service import TargetService
from app.utils.transform import get_perspective_transform, transform_points
from app.services.registry import registry

import time

router = APIRouter()
target_service = TargetService()

@router.get("/corners/{cam_id}")
def target_corners(cam_id,tw: int = Query(...), th: int = Query(...)):
    frame_manager = registry.get_camera(cam_id)
    if not frame_manager:
        raise HTTPException(status_code=404, detail=f"Camera {cam_id} not found")
    frame = None
    src_pts = None
  
    for _ in range(50):
        frame = frame_manager.get_frame()
        if frame is not None:
            src_pts = target_service.get_target_raw(frame)
            if src_pts:
                M, dst_pts = get_perspective_transform(src_pts, tw, th)
                corners = transform_points(src_pts, M)
                return {"corners": corners}

        time.sleep(0.1)  

  
    return {"corners": []}


