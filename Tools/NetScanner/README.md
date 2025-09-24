# ns (nscan) - Simple Network Scanner with Banner Grab

`ns` は Python で作ったシンプルなネットワークスキャナーです。  
TCP ポートの開閉確認に加え、オプションでサービスバナーを取得してサービス名やバージョンを確認できます。

---

## 機能

- TCP ポートスキャン（WELL-KNOWN ポート 0-1023 デフォルト）
- 全ポートスキャン（0-65535）対応
- 任意ポート指定スキャン
- サービスバナー取得オプション
- Nmap 風の出力フォーマット

---

## インストール

Python 3 がインストールされていれば追加依存なしで使用可能です。

```bash
git clone <リポジトリURL>
cd ns
chmod +x ns.py
```

## 使い方
基本スキャン
```bash
./ns.py 10.10.10.5
```

全ポートスキャン
```bash
./ns.py 10.10.10.5 --all
```

任意ポート指定
```bash
./ns.py 10.10.10.5 --ports 22,80,443
```

サービスバナー取得
```bash
./ns.py 10.10.10.5 --service
```
##オプション一覧
```bash
オプション	説明
<IP>	スキャン対象の IP アドレス
--all	全ポート（0-65535）をスキャン
--ports	カンマ区切りで任意ポート指定
--service	バナー取得でサービス名・バージョン表示
```

## 注意事項
- 自分が所有・許可された環境でのみ使用してください
- 無許可のスキャンは違法です
- タイムアウト値やスレッド数はコード内で調整可能
- バナーが返らないポートもあります
- 高速・全ポートスキャンではターゲットに負荷がかかります

## 出力例
```bash
ns scan report for 10.10.10.5
Host is up (0.53s latency).
Not shown: 1022 closed tcp ports (conn-refused)

PORT     STATE    SERVICE      VERSION
22/tcp   open     ssh          SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.11
80/tcp   open     http         Apache/2.4.41 (Ubuntu)

Scan done: 1 IP address (1 host up) scanned in 3.75 seconds
```

## 参考
- Python socket モジュール
- ThreadPoolExecutor による並列スキャン
- Nmap 風出力フォーマット