"""
FastAPI 启动前必须先成功导入所有被 main.py 和 router 引用的模块。
只要某个被 import 的文件有代码错误，app 对象就创建失败，uvicorn 就无法启动。
启动成功后，具体接口错误才会表现为某个请求失败。
"""


import uvicorn


if __name__ == "__main__":
    #前面的 app.main 是 Python 模块路径。找到其中的app对象运行。
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
