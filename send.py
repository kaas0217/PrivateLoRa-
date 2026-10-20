import argparse
import time

import serial

from lora_frame import build_frame


def main():
    p = argparse.ArgumentParser(description="E220 で文字列を送信")
    p.add_argument("text", help="送信する文字列")
    p.add_argument("--port", default="/dev/ttyUSB0")
    p.add_argument("--baud", type=int, default=9600)
    p.add_argument("--src", type=int, default=1)
    p.add_argument("--dst", type=int, default=2)
    p.add_argument("--count", type=int, default=1, help="連番を増やしながら送る回数")
    p.add_argument("--interval", type=float, default=3.0, help="送信間隔(秒)")
    args = p.parse_args()

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        for seq in range(args.count):
            frame = build_frame(args.src, args.dst, seq, args.text)
            ser.write(frame)
            print(f"sent seq={seq} ({len(frame)} bytes)")
            if seq < args.count - 1:
                time.sleep(args.interval)


if __name__ == "__main__":
    main()
