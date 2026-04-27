import websockets
import asyncio
import pyaudio
import audioop


async def data_reciever(connect,stream):
    async for data in connect:
        if isinstance(data, bytes):
            data2 = audioop.ulaw2lin(data,4)
            stream.write(data2)
            print(f"{data}")
        else:
            print(f"{data}")

async def test_tts_client():
    local_websocket = 'ws://127.0.0.1:8000/ws/tts?aura-2-thalia-en'

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 24000
    CHUNK = 1024
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)
    try:
        async with websockets.connect(local_websocket) as connect:
            print(f"Client Websocket Connected")               
            reciever = asyncio.create_task(data_reciever(connect,stream))

            text = "Hello, how can I help you today? My name is Emily and I'm very glad to meet you. What do you think of this new text-to-speech API?"
            await connect.send(text)
            print(f"Sent: {text}")
            await asyncio.sleep(20) 
            reciever.cancel()
            
    except Exception as e:
        print(f"Client WebSocket error: {e}")
    
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    
if __name__=='__main__':
    asyncio.run(test_tts_client())
