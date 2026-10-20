# lora-e220-raspi

Raspberry Pi 同士を、EBYTE E220 (USBドングル) の LoRa で通信して文字列を送るサンプル。

## 仕組み

LoRa が運ぶのはただのバイト列なので、文字列は UTF-8 にして、簡単なヘッダと CRC を付けて送る。

```
[送信元 1B][宛先 1B][連番 1B][長さ 1B][本文 nB][CRC16 2B]
```

- 本文は UTF-8(日本語は 1文字3バイト)。最大200バイトに制限
- CRC で破損パケットを検出して捨てる
- 連番で取りこぼしを検知できる

## 準備

```bash
pip install -r requirements.txt
sudo usermod -aG dialout $USER   # ログインし直す
```

E220 の設定(チャンネル、エアデータレート、アドレス、暗号キー)は **送受信で揃える**こと。
通常送受信はモード M0=M1=0。

## 使い方

受信側:

```bash
python receive.py --port /dev/ttyUSB0
```

送信側:

```bash
python send.py "こんにちは" --port /dev/ttyUSB0
python send.py "test" --count 10 --interval 5
```

E220 の RSSI バイトを有効にしている場合は、受信側に `--rssi` を付ける。

## 注意

- 日本では 920MHz 帯の日本向けモデル(技適付き)を使い、LBT・送信時間制限などの規定を守ること
- UART はバイトの流れなので、同期ずれが起きると以降のフレームが読めなくなる。必要なら同期バイトや COBS を追加する
- 複数台で使う場合は、E220 の固定送信モードや自前の宛先フィルタを検討する
