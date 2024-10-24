    #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
    #                   _oo0oo_
    #                   o8888888o
    #                   88" . "88
    #                   (| -_- |)
    #                   0\  =  /0
    #                 ___/`---'\___
    #               .' \\|     |// '.
    #              / \\|||  :  |||// \
    #             / _||||| -:- |||||- \
    #            |   | \\\  - /// |   |
    #            | \_|  ''\---/''  |_/ |
    #            \  .-\__  '-'  ___/-. /
    #          ___'. .'  /--.--\  `. .'___
    #       ."" '<  `.___\_<|>_/___.' >' "".
    #      | | :  `- \`.;`\ _ /`;.`/ - ` : | |
    #      \  \ `_.   \_ __\ /__ _/   .-` /  /
    #  =====`-.____`.___ \_____/___.-`___.-'=====
    #                    `=---='

    #    此專案被 南無BUG菩薩保佑，不當機，不報錯
    #  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
from fastapi import FastAPI, WebSocket, APIRouter
from fastapi.staticfiles import StaticFiles
from llm.Interface import llm_interface
from llm.LlamaAPI import llm_api
from tts.tts import tts
from scripts.PorjectBlesser import blessing
import uvicorn
import argparse
import yaml
import asyncio

class web_app():
    def __init__(self, path=r'.\config.yaml'):
        self.load_cfg(path)
        self.app = FastAPI()
        self.router = APIRouter()

        # connect to index.html
        self.set_routes()

        self.app.mount("/", StaticFiles(directory="./web", html=True), name="web")
        self.app.mount("/", StaticFiles(directory="./audio"), name="audio")

        self.app.include_router(self.router)

        self.llm = self.init_llm(self.args.llm_url, self.args.api_key, self.args.model, self.args.organization_id, self.args.project_id)
        self.tts = self.init_tts(self.args.tts_mode, self.args.edge)

    def init_llm(self, llm_url, api_key, model, org_id, pro_id, system='You are a sarcastic and sexy AI chatbot who loves to the jokes "Get out and touch some grass"') -> llm_interface:
        self.callback(f"connect to llm llm_url:{llm_url}")
        self.callback(f"api_key:{api_key}, model:{model}")
        return llm_api(
        llm_url=llm_url,
        model=model,
        api_key=api_key,
        org=org_id,
        project=pro_id,
        system=system )
    
    def init_tts(self, tts_type, config):
        self.callback(f'TTS type: {tts_type}. Config: {config}')
        return tts.init(tts_type=tts_type, **config)

    def set_routes(self):
        @self.app.websocket("/llm-ws")    
        async def websocket_handler(websocket: WebSocket,): # 不能使用 self
            await websocket.accept()
            print("[DeBug] [WebSocket] | WebSocket connection established")
            
            # 持續接收客戶端消息
            while True:
                try:
                    text = ''
                    data = await websocket.receive_text()
                    print(f"[DeBug] [WebSocket] | Received: {data} send to llm...")
                    res = self.llm.chat_iter(str(data))
                    
                    for chunk in res:
                        if chunk:
                            text += chunk

                    self.tts.generate_audio(str(text))

                    await websocket.send_text(f"Audio file: ./audio/tts_audio.mp3")

                    print(f"[DeBug] [WebSocket] | Response: {text}")

                    await websocket.send_text(f"Message res: {text}")
                except Exception as e:
                    print(f"[DeBug] [WebSocket] | WebSocket error: {e}")
                    break
            await websocket.close()

    def load_cfg(self, path):
        config = yaml.load(open(path, 'r', encoding='UTF-8'), Loader=yaml.FullLoader)
        self.args = argparse.Namespace(**config)
        self.callback("config loaded")

    def callback(self, msg):
        print(f'[DeBug] [WebSocket] | {msg}')

    def start_server(self):
        uvicorn.run(self.app, host="127.0.0.1", port=self.args.port)

if __name__ == "__main__":
    run = web_app()
    run.start_server()

    if run.args.bless:
        blessing()