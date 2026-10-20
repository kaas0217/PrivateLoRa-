import argparse

import serial

from lora_frame import read_frame


def main():
    p = argparse.ArgumentParser(description="E220 で受信して表示")
    p.add_argument("--port", default="/dev/ttyUSB0")
    p.add_argument("--baud", type=int, default=9600)
    p.add_argument("--rssi", action="store_true", help="E220のRSSIバイト有効時に指定")
    args = p.parse_args()

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        print(f"listening on {args.port} ...")
        while True:
            frame = read_frame(ser, rssi_byte=args.rssi)
            if frame:
                src, dst, seq, text = frame
                print(f"from={src} to={dst} seq={seq} text={text}")


if __name__ == "__main__":
    main()
