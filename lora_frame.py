"""LoRa (E220 など UART 透過モード) 用の簡易フレーム処理。

フレーム構成:
    [送信元 1B][宛先 1B][連番 1B][長さ 1B][本文 nB][CRC16 2B]

本文は UTF-8 文字列。CRC は CRC-CCITT (binascii.crc_hqx)。
"""
import binascii
import struct

HEADER_SIZE = 4
CRC_SIZE = 2
MAX_BODY = 200  # E220 のサブパケットサイズ(初期値200B)に収める


def build_frame(src: int, dst: int, seq: int, text: str) -> bytes:
    body = text.encode("utf-8")
    if len(body) > MAX_BODY:
        raise ValueError(f"本文が長すぎます: {len(body)} > {MAX_BODY} bytes")
    header = struct.pack("!BBBB", src, dst, seq & 0xFF, len(body))
    crc = binascii.crc_hqx(header + body, 0)
    return header + body + struct.pack("!H", crc)


def parse_frame(data: bytes):
    """bytes 1フレーム分を (src, dst, seq, text) にする。CRC不一致は ValueError。"""
    src, dst, seq, length = struct.unpack("!BBBB", data[:HEADER_SIZE])
    body = data[HEADER_SIZE:HEADER_SIZE + length]
    (crc,) = struct.unpack("!H", data[HEADER_SIZE + length:HEADER_SIZE + length + CRC_SIZE])
    if binascii.crc_hqx(data[:HEADER_SIZE + length], 0) != crc:
        raise ValueError("CRC error")
    return src, dst, seq, body.decode("utf-8")


def read_frame(ser, rssi_byte: bool = False):
    """シリアルから1フレーム読む。タイムアウト/CRC不一致は None。

    rssi_byte=True の場合、E220 の RSSI バイト(末尾1B)を読み捨てる。
    """
    header = ser.read(HEADER_SIZE)
    if len(header) < HEADER_SIZE:
        return None
    _, _, _, length = struct.unpack("!BBBB", header)
    rest = ser.read(length + CRC_SIZE + (1 if rssi_byte else 0))
    if len(rest) < length + CRC_SIZE:
        return None
    try:
        return parse_frame(header + rest[:length + CRC_SIZE])
    except (ValueError, UnicodeDecodeError, struct.error):
        return None
