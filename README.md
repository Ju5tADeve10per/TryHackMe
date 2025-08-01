# TryHackMe
WriteUps

Write Up's Template
# Room Title - TryHackMe Writeup

> ⚠️ **This writeup is for educational purposes only.**
> It does not contain any flags or direct solutions.  
> Please do not use it to spoil the challenge for others.

---

## 🏷️ Room: [Room Name](https://tryhackme.com/room/roomname)
- **Category**: [e.g. Linux, Web, Forensics, etc.]
- **Difficulty**: [Easy / Medium / Hard]
- **Date Completed**: YYYY-MM-DD

---

## 🧠 Goal

このルームでは、以下の技術や知識の習得を目指しました：

- [x] ポートスキャンとサービス調査
- [x] ディレクトリブルートフォース
- [x] 特権昇格（Privilege Escalation）
- [x] [追加要素があれば記載]

---

## 🛠 使用ツール・コマンド例

| ツール | 用途 |
|--------|------|
| `nmap` | ポートスキャン |
| `gobuster` | Webディレクトリ探索 |
| `linpeas` | ローカル権限昇格の調査 |
| `netcat` | リバースシェル通信 |
| その他 | 例：`hydra`, `sqlmap`, `ftp`, etc. |

---

## 🚩 攻略手順（概要）

### 🔍 1. ポートスキャン
```bash
nmap -sC -sV -oN scan.txt 10.10.X.X

以後一問ずつ解き方を解説