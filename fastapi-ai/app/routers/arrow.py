from fastapi import APIRouter

router = APIRouter()
#TODO: 추후 명중 결과 db에 남길때 HTTP 로 사용
@router.get("/arrow-detect")
def arrow_save():
    return None
