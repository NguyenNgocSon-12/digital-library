#!/usr/bin/env python3
"""Seed dữ liệu Redis bằng bookId thật từ MongoDB (Phase 1 – Đạt, phối hợp Sơn, barem mục 4).

Đặc điểm:
  * Chạy sau `seed_books.py`: đọc `book_ids.json` và kiểm tra từng sách có thật trong MongoDB.
  * Tạo 10 độc giả mẫu (`reader01`…`reader10`, mật khẩu `reader123`) với ID cố định
    (`5eed` + số thứ tự) để tiến trình đọc trỏ tới user có thật và đăng nhập demo được.
  * Ghi ≥ 50 Hash `progress:{userId}:{bookId}` (chapter, page, line, updatedAt) đúng quy ước
    docs/SHARED.md; số chương không vượt số chương thật của sách.
  * Ghi ZSET `ranking:books` gồm 50 sách bằng `ZADD` (đặt điểm, không cộng dồn) nên chạy lại
    cho cùng kết quả. Lượt đọc thật sau đó vẫn tăng qua `POST /api/books/{bookId}/read`.
  * Chỉ ghi/xóa key của user seed và member là sách seed; không đụng phiên đăng nhập hay dữ liệu khác.

Dùng:
  python seed_redis.py                 # nạp user mẫu + Redis
  python seed_redis.py --reset         # xóa tiến trình của user seed và điểm của sách seed rồi nạp lại
  python seed_redis.py --dry-run       # chỉ sinh dữ liệu, không ghi
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import bcrypt
    from bson import ObjectId
except ImportError:  # pragma: no cover
    sys.exit("Thiếu thư viện. Chạy: pip install -r requirements.txt")

HERE = Path(__file__).resolve().parent
IDS_PATH = HERE / "book_ids.json"
USER_ID_PREFIX = "5eed"  # ObjectId = prefix + 20 chữ số hex của số thứ tự → ổn định giữa các lần chạy
USER_COUNT = 10
BOOKS_PER_USER = 6  # 10 × 6 = 60 Hash tiến trình
RANKING_SIZE = 50
RANKING_KEY = "ranking:books"
DEFAULT_PASSWORD = "reader123"
DEFAULT_MONGO_URI = "mongodb://admin:admin123@localhost:27017/digital_library?authSource=admin"
DEFAULT_REDIS_URL = "redis://localhost:6379"
USER_CLASS = "vn.edu.huit.digitallibrary.identity.model.User"  # giống document Spring Data ghi

FULL_NAMES = [
    "Nguyễn Minh Anh", "Trần Gia Bảo", "Lê Thu Hà", "Phạm Quốc Huy", "Hoàng Ngọc Lan",
    "Vũ Đức Long", "Đặng Thảo My", "Bùi Hải Nam", "Đỗ Khánh Vy", "Ngô Tuấn Kiệt",
]


def iso_utc(dt: datetime) -> str:
    # Cùng định dạng Instant.toString() của backend: 2026-10-22T06:00:00Z
    return dt.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_users(now: datetime) -> list[dict]:
    password_hash = bcrypt.hashpw(DEFAULT_PASSWORD.encode(), bcrypt.gensalt(rounds=10)).decode()
    created = now.replace(microsecond=0)
    return [
        {
            "_id": ObjectId(f"{USER_ID_PREFIX}{i:020x}"),
            "username": f"reader{i:02d}",
            "email": f"reader{i:02d}@digital-library.local",
            "passwordHash": password_hash,
            "fullName": FULL_NAMES[i - 1],
            "role": "USER",
            "createdAt": created,
            "updatedAt": created,
            "_class": USER_CLASS,
        }
        for i in range(1, USER_COUNT + 1)
    ]


def make_progress(users: list[dict], books: list[dict], rng: random.Random, now: datetime) -> dict[str, dict]:
    """Mỗi user đọc dở BOOKS_PER_USER sách khác nhau; các user trải đều trên kho sách."""
    progress = {}
    for u, user in enumerate(users):
        for k in range(BOOKS_PER_USER):
            book = books[(u * BOOKS_PER_USER + k) % len(books)]
            key = f"progress:{user['_id']}:{book['bookId']}"
            progress[key] = {
                "chapter": str(rng.randint(1, book["chapterCount"])),
                "page": str(rng.randint(1, 40)),
                "line": str(rng.randint(0, 30)),
                "updatedAt": iso_utc(now - timedelta(minutes=rng.randint(5, 14 * 24 * 60))),
            }
    return progress


def make_ranking(books: list[dict], rng: random.Random) -> dict[str, float]:
    # Phân bố lệch như thực tế: vài sách rất hot, phần lớn ít lượt đọc
    return {b["bookId"]: float(int(rng.paretovariate(1.2) * 10)) for b in books[:RANKING_SIZE]}


def load_books(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"Không thấy {path}. Hãy chạy `python seed_books.py` trước.")
    books = json.loads(path.read_text(encoding="utf-8"))
    if len(books) < RANKING_SIZE:
        sys.exit(f"Cần ít nhất {RANKING_SIZE} sách seed, {path.name} chỉ có {len(books)}.")
    return books


def verify_books_in_mongo(db, books: list[dict]) -> None:
    ids = [ObjectId(b["bookId"]) for b in books]
    found = {
        str(d["_id"]): len(d.get("chapters", []))
        for d in db.books.find({"_id": {"$in": ids}}, {"chapters.chapterNo": 1})
    }
    missing = [b["bookId"] for b in books if b["bookId"] not in found]
    if missing:
        sys.exit(f"{len(missing)} bookId chưa có trong MongoDB (vd {missing[0]}). Chạy lại `python seed_books.py`.")
    for b in books:  # dùng số chương thật trong DB, phòng khi admin đã sửa sách
        b["chapterCount"] = found[b["bookId"]]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=2026, help="hạt giống ngẫu nhiên, cùng seed → cùng dữ liệu")
    ap.add_argument("--mongo-uri", default=os.environ.get("MONGO_URI", DEFAULT_MONGO_URI), help="mặc định lấy MONGO_URI")
    ap.add_argument("--redis-url", default=os.environ.get("REDIS_URL", DEFAULT_REDIS_URL), help="mặc định lấy REDIS_URL")
    ap.add_argument("--ids", default=str(IDS_PATH), help="file bookId do seed_books.py xuất")
    ap.add_argument("--reset", action="store_true", help="xóa dữ liệu Redis seed cũ trước khi nạp")
    ap.add_argument("--dry-run", action="store_true", help="chỉ sinh dữ liệu, không ghi MongoDB/Redis")
    args = ap.parse_args()

    rng = random.Random(f"{args.seed}-redis")
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    books = load_books(Path(args.ids))
    users = make_users(now)

    if args.dry_run:
        progress = make_progress(users, books, rng, now)
        ranking = make_ranking(books, rng)
        print(f"--dry-run: {len(users)} user, {len(progress)} Hash tiến trình, ZSET {len(ranking)} sách. Không ghi DB.")
        return

    import redis
    from pymongo import MongoClient, ReplaceOne
    from pymongo.errors import PyMongoError

    client = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except PyMongoError as ex:
        sys.exit(f"Không kết nối được MongoDB ({ex.__class__.__name__}). Xem mục xử lý lỗi cổng 27017 trong docs/SHARED.md.")
    db = client.get_default_database(default="digital_library")
    verify_books_in_mongo(db, books)

    r = redis.Redis.from_url(args.redis_url, decode_responses=True)
    try:
        r.ping()
    except redis.RedisError as ex:
        sys.exit(f"Không kết nối được Redis ({ex.__class__.__name__}). Đã chạy `docker compose up -d` chưa?")

    progress = make_progress(users, books, rng, now)
    ranking = make_ranking(books, rng)

    # Độc giả mẫu: upsert theo _id; giữ createdAt cũ nếu đã có để chạy lại không đổi lịch sử
    existing = {d["_id"]: d["createdAt"] for d in db.users.find({"_id": {"$in": [u["_id"] for u in users]}}, {"createdAt": 1})}
    for u in users:
        u["createdAt"] = existing.get(u["_id"], u["createdAt"])
    db.users.bulk_write([ReplaceOne({"_id": u["_id"]}, u, upsert=True) for u in users], ordered=False)

    pipe = r.pipeline(transaction=False)
    if args.reset:
        for u in users:
            for key in r.scan_iter(match=f"progress:{u['_id']}:*", count=500):
                pipe.delete(key)
        pipe.zrem(RANKING_KEY, *[b["bookId"] for b in books])
    for key, fields in progress.items():
        pipe.hset(key, mapping=fields)
    pipe.zadd(RANKING_KEY, ranking)
    pipe.execute()

    hashes = sum(1 for u in users for _ in r.scan_iter(match=f"progress:{u['_id']}:*", count=500))
    top = r.zrevrange(RANKING_KEY, 0, 2, withscores=True)
    print(f"MongoDB: {len(users)} độc giả mẫu (reader01…reader{USER_COUNT:02d} / {DEFAULT_PASSWORD}).")
    print(f"Redis: {hashes} Hash progress:* của user seed; {RANKING_KEY} có {r.zcard(RANKING_KEY)} sách, "
          f"top 3 = {[(m, int(s)) for m, s in top]}")


if __name__ == "__main__":
    main()
