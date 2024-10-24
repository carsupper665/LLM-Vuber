from typing import Type

class tts:
    @staticmethod
    def init(tts_type, **args):
        if tts_type == 'edgeTTS':
            from .EdgeTts import EdgeTTS
            return EdgeTTS(args.get('voice'), args.get('pitch'))
        else:
            raise ValueError(f"[DeBug] [TTS] | Unknown TTS engine type: {tts_type}")