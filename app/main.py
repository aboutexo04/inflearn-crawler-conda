from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from app.crawler import search_inflearn_courses
import os

app = FastAPI(
    title="인프런 강의 검색 API",
    description="인프런에서 강의를 검색하고 결과를 반환하는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class SearchRequest(BaseModel):
    keyword: str
    max_results: int = 20

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """메인 페이지 반환"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>인프런 강의 검색</title></head>
            <body>
                <h1>인프런 강의 검색 서비스</h1>
                <p>frontend/index.html 파일이 없습니다.</p>
                <p><a href="/docs">API 문서 보기</a></p>
            </body>
        </html>
        """)

@app.get("/search")
async def search_courses(
    keyword: str = Query(..., description="검색할 키워드"),
    max_results: int = Query(20, description="최대 결과 수", ge=1, le=50)
):
    """
    인프런에서 강의를 검색합니다.
    
    - **keyword**: 검색할 키워드 (필수)
    - **max_results**: 최대 결과 수 (1-50, 기본값: 20)
    """
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="검색 키워드를 입력해주세요.")
    
    try:
        results = search_inflearn_courses(keyword.strip(), max_results)
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        
        return {
            "success": True,
            "keyword": keyword,
            "total_results": results["total_results"],
            "courses": results["courses"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@app.post("/search")
async def search_courses_post(request: SearchRequest):
    """
    POST 방식으로 인프런에서 강의를 검색합니다.
    """
    if not request.keyword.strip():
        raise HTTPException(status_code=400, detail="검색 키워드를 입력해주세요.")
    
    try:
        results = search_inflearn_courses(request.keyword.strip(), request.max_results)
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        
        return {
            "success": True,
            "keyword": request.keyword,
            "total_results": results["total_results"],
            "courses": results["courses"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "message": "서버가 정상적으로 동작 중입니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
