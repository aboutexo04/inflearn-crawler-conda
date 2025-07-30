#!/usr/bin/env python3
"""
간단한 HTTP 서버로 인프런 크롤링 테스트
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from app.crawler import search_inflearn_courses

class CrawlerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # HTML 페이지 반환
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>인프런 강의 검색</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        input[type="text"] { width: 300px; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
        .result { margin-top: 30px; padding: 20px; border: 1px solid #ddd; }
        .course { margin-bottom: 20px; padding: 15px; border-left: 4px solid #007bff; background: #f9f9f9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 인프런 강의 검색</h1>
        <div>
            <input type="text" id="keyword" placeholder="검색할 키워드를 입력하세요" value="파이썬">
            <button onclick="search()">검색</button>
        </div>
        <div id="results"></div>
    </div>
    
    <script>
        function search() {
            const keyword = document.getElementById('keyword').value;
            if (!keyword) {
                alert('키워드를 입력하세요');
                return;
            }
            
            document.getElementById('results').innerHTML = '<p>검색 중...</p>';
            
            fetch(`/search?keyword=${encodeURIComponent(keyword)}`)
                .then(response => response.json())
                .then(data => {
                    let html = '<div class="result">';
                    html += `<h3>"${data.keyword}" 검색 결과 (총 ${data.total_results}개)</h3>`;
                    
                    if (data.courses && data.courses.length > 0) {
                        data.courses.forEach((course, index) => {
                            html += `<div class="course">`;
                            html += `<h4>${index + 1}. ${course.title || '제목 없음'}</h4>`;
                            html += `<p><strong>강사:</strong> ${course.instructor || '정보 없음'}</p>`;
                            html += `<p><strong>가격:</strong> ${course.price || '정보 없음'}</p>`;
                            if (course.url) {
                                html += `<p><a href="${course.url}" target="_blank">강의 보러가기</a></p>`;
                            }
                            html += `</div>`;
                        });
                    } else {
                        html += '<p>검색 결과가 없습니다.</p>';
                        if (data.error) {
                            html += `<p style="color: red;">오류: ${data.error}</p>`;
                        }
                    }
                    html += '</div>';
                    
                    document.getElementById('results').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('results').innerHTML = `<p style="color: red;">오류: ${error}</p>`;
                });
        }
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path.startswith('/search'):
            # 크롤링 API
            try:
                parsed_url = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed_url.query)
                keyword = params.get('keyword', [''])[0]
                
                if not keyword:
                    self.send_error(400, "키워드가 필요합니다")
                    return
                
                # 크롤링 실행 (더 많은 결과)
                result = search_inflearn_courses(keyword, 10)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                error_response = {"error": str(e), "keyword": keyword, "courses": []}
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404, "페이지를 찾을 수 없습니다")

def run_server():
    server_address = ('127.0.0.1', 9000)
    httpd = HTTPServer(server_address, CrawlerHandler)
    print(f"서버 시작: http://127.0.0.1:9000")
    print("브라우저에서 http://localhost:9000 으로 접속하세요")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()