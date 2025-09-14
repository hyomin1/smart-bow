import cv2
import numpy as np

def get_perspective_transform(src_pts, width=500, height=500):
    """
    src_pts: 원본 과녁 꼭짓점 (4점)
    width, height: 보정할 직사각형 크기
    return: (M, dst_pts)
    """
    src = np.array(src_pts, dtype=np.float32)
    dst = np.array([[0,0],[width,0],[width,height],[0,height]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    return M, dst

def warp_frame(frame, M, width=500, height=500):
    """프레임 보정"""
    return cv2.warpPerspective(frame, M, (width, height))

def transform_points(points, M):
    """좌표(points)를 변환 행렬 M으로 보정"""
    pts = np.array(points, dtype=np.float32).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M)
    return dst.reshape(-1,2).tolist()
