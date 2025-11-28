import time
import json
import cv2
from websocket import create_connection

WS_URL = "ws://127.0.0.1:8000/v1/infer/ws/session/sess-pc-test"

def main():
    print(f"Conectando em {WS_URL} ...")
    ws = create_connection(WS_URL)
    print("Conectado!")

    cap = cv2.VideoCapture(0)  # webcam padrão
    if not cap.isOpened():
        print("Não conseguiu abrir a webcam. Verifique se há câmera disponível.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao capturar frame")
                break

            # Opcional: reduzir resolução para algo próximo de 480p
            frame = cv2.resize(frame, (640, 480))

            # Codifica em JPEG
            ok, buf = cv2.imencode(".jpg", frame)
            if not ok:
                print("Falha ao codificar JPEG")
                continue

            jpeg_bytes = buf.tobytes()

            # Envia frame binário pelo WS
            ws.send(jpeg_bytes, opcode=0x2)  # 0x2 = binário

            # Tenta ler resposta (não bloqueando demais)
            ws.settimeout(0.5)
            try:
                msg = ws.recv()
                try:
                    data = json.loads(msg)
                    if data.get("type") == "metrics":
                        print(
                            f"reps={data.get('reps')}, "
                            f"rom={data.get('rom'):.1f}, "
                            f"cadence={data.get('cadence')}, "
                            f"alerts={data.get('alerts')}"
                        )
                    else:
                        print("Mensagem não-métricas:", data)
                except json.JSONDecodeError:
                    print("Recebeu texto não-JSON:", msg)
            except Exception:
                # Sem mensagem no timeout, segue o loop
                pass

            # ~10 fps
            time.sleep(0.1)

    finally:
        cap.release()
        ws.close()
        print("Encerrado.")

if __name__ == "__main__":
    main()
