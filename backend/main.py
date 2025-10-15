# main.py
# uvicorn 서버를 실행하는 시작점입니다.
import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)

