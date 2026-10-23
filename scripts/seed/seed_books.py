#!/usr/bin/env python3
"""Seed dữ liệu mẫu cho collection `books` của MongoDB (Phase 1 – Sơn, barem mục 4).

Đặc điểm:
  * Sinh 60 đầu sách (mặc định), mỗi sách 5–10 chương toàn văn, mỗi chương 2–4 mục.
  * Chạy lặp được: ID sách cố định theo thứ tự (`b00c` + số thứ tự), ghi bằng upsert
    nên chạy lại chỉ ghi đè đúng các sách seed, không nhân đôi, không đụng sách khác.
  * Không cần mạng, không cần faker: nội dung tiếng Việt sinh theo thể loại, cùng
    `--seed` cho ra cùng dữ liệu.
  * Kiểu dữ liệu khớp validator `books.schema.json`: chapterNo/sectionNo là int32,
    createdAt/updatedAt là date. Script tự kiểm tra trước khi ghi.
  * Xuất `book_ids.json` để Đạt seed Redis bằng bookId thật.

Dùng:
  python seed_books.py                 # nạp 60 sách vào MongoDB
  python seed_books.py --count 80      # nạp 80 sách
  python seed_books.py --reset         # xóa các sách seed cũ rồi nạp lại
  python seed_books.py --dry-run       # chỉ sinh + kiểm tra schema, không kết nối Mongo
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
    from bson import ObjectId
except ImportError:  # pragma: no cover
    sys.exit("Thiếu pymongo. Chạy: pip install -r requirements.txt")

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE.parent.parent / "backend/src/main/resources/mongo/books.schema.json"
IDS_PATH = HERE / "book_ids.json"
ID_PREFIX = "b00c"  # ObjectId = prefix + 20 chữ số hex của số thứ tự → ổn định giữa các lần chạy
DEFAULT_URI = "mongodb://admin:admin123@localhost:27017/digital_library?authSource=admin"

# ---------------------------------------------------------------- dữ liệu nguồn

NARRATIVE = {
    "Văn học": dict(
        P=["bà Tám", "ông giáo Hòa", "cô Thu", "anh Lâm", "chị Hạnh", "bác lái đò", "cậu học trò", "dì Năm"],
        L=["xóm nhỏ ven sông", "con ngõ cuối phố", "ngôi làng bên chân đồi", "bến đò cũ", "mái hiên ga tàu", "căn nhà ba gian"],
        O=["chiếc hộp gỗ cũ", "bức thư chưa gửi", "cây đàn bầu", "chiếc áo dài phai màu", "cuốn sổ tay ngả vàng", "ngọn đèn dầu"],
        A=["tình thân", "nỗi nhớ quê", "sự tha thứ", "những lựa chọn đã qua", "lòng tự trọng", "niềm hy vọng"],
    ),
    "Khoa học viễn tưởng": dict(
        P=["thuyền trưởng Minh", "kỹ sư Lan", "nhà sinh học Quân", "trí tuệ nhân tạo Mây", "phi công Khôi", "giáo sư Đài"],
        L=["trạm không gian Hải Vân", "thành phố nổi trên mây", "hành tinh Thiên Lam", "khu thí nghiệm ngầm", "con tàu thế hệ", "vành đai tiểu hành tinh"],
        O=["chiếc máy dịch thời gian", "tín hiệu lạ từ vũ trụ", "lõi năng lượng cũ", "tấm bản đồ sao thất lạc", "cánh cổng lượng tử", "bộ nhớ sinh học"],
        A=["ranh giới giữa người và máy", "cái giá của tiến bộ", "ký ức nhân tạo", "quyền được lựa chọn", "sự cô độc giữa các vì sao", "tương lai của loài người"],
    ),
    "Trinh thám": dict(
        P=["thám tử Phong", "thanh tra Hà", "nữ phóng viên Vy", "ông chủ tiệm đồng hồ", "trung úy Sơn", "luật sư Khánh"],
        L=["căn biệt thự bỏ hoang", "con phố cổ về đêm", "ga tàu cuối tuyến", "hiệu sách cũ", "cảng sông vắng người", "khách sạn ven biển"],
        O=["chiếc chìa khóa lạ", "tờ giấy bị xé dở", "bức ảnh chụp lén", "chiếc đồng hồ dừng giờ", "cuốn nhật ký mất trang", "chiếc va li khóa kín"],
        A=["sự thật bị chôn giấu", "động cơ thật sự", "lời khai mâu thuẫn", "dấu vết cuối cùng", "lòng tin giữa đồng đội", "bóng dáng kẻ vắng mặt"],
    ),
    "Lịch sử": dict(
        P=["vị tướng trẻ", "viên quan thanh liêm", "người lính biên cương", "bà đồ già", "sứ giả triều đình", "thầy lang làng"],
        L=["kinh thành xưa", "ải biên giới", "dòng sông lịch sử", "doanh trại bên sườn núi", "ngôi đình làng", "bến cảng cổ"],
        O=["tấm bản đồ cổ", "đạo sắc phong", "thanh gươm gỉ sét", "tấm bia đá rêu phong", "bức mật thư", "chiếc trống đồng"],
        A=["vận nước", "lòng dân", "nghĩa vụ với quê hương", "cái giá của hòa bình", "sự trung thành", "bài học của người đi trước"],
    ),
    "Thiếu nhi": dict(
        P=["bé Na", "chú mèo Mướp", "cậu bé Tí", "bạn Sóc nâu", "cô bé Bông", "chú gấu Mật"],
        L=["khu vườn sau nhà", "khu rừng nhỏ", "bãi cỏ đầu làng", "con suối trong veo", "ngôi trường làng", "gốc cây đa"],
        O=["chiếc cầu vồng nhỏ", "hạt giống kỳ diệu", "chiếc diều giấy", "quả bóng đỏ", "chiếc ô vàng", "chiếc chuông gió"],
        A=["tình bạn", "sự dũng cảm", "lòng tốt", "niềm vui chia sẻ", "tính trung thực", "tinh thần giúp đỡ nhau"],
    ),
    "Du ký": dict(
        P=["người viết", "anh bạn đồng hành", "cô hướng dẫn viên", "bác tài xế", "đoàn lữ khách", "ông chủ homestay"],
        L=["thị trấn ven biển", "cao nguyên mờ sương", "chợ phiên vùng cao", "con đường xuyên rừng", "bến xe sớm mai", "làng chài đầu vịnh"],
        O=["chiếc ba lô sờn vai", "tấm bản đồ gấp nếp", "bát phở nóng", "chuyến xe đêm", "tấm vé tàu cũ", "chiếc máy ảnh film"],
        A=["niềm vui của những chuyến đi", "vẻ đẹp của sự giản dị", "tình hiếu khách", "cảm giác lạc đường", "ý nghĩa của việc trở về", "sự tò mò"],
    ),
}

NARR_V = [
    "nằm yên ở đó suốt nhiều năm", "chứng kiến biết bao đổi thay", "thay đổi cách mọi người nhìn nhau",
    "giữ lại một phần ký ức của cả vùng", "khiến nhiều người mất ngủ", "đi qua tay không ít người",
]
NARR_T = ["sáng sớm", "chiều muộn", "đêm khuya", "một ngày cuối thu", "mùa mưa năm ấy", "buổi trưa lặng gió"]
NARR_W = ["bóng chiều", "màn đêm", "cơn mưa đầu mùa", "làn sương mỏng", "ánh trăng non"]
NARR_Q = [
    "Mọi chuyện rồi sẽ có lời giải", "Tôi chưa từng nghĩ mình sẽ quay lại nơi này",
    "Đừng vội, hãy nghe hết câu chuyện đã", "Có những điều chỉ hiểu khi đã đi đủ xa",
    "Chúng ta không còn nhiều thời gian", "Nếu có thể, tôi vẫn chọn đi lại từ đầu",
]
NARR_TPL = [
    "{P} đứng lặng trước {O} ở {L}, nghĩ về {A}.",
    "Vào {T}, {P} trở lại {L} và nhận ra {A} chưa bao giờ đơn giản như mình từng tưởng.",
    "Không ai ở {L} biết rằng {O} đã {V}.",
    "\"{Q},\" {P} nói khẽ, mắt vẫn nhìn về phía {L}.",
    "{P} và {P2} cùng im lặng hồi lâu, chỉ còn tiếng gió lùa qua {L}.",
    "Càng đi sâu vào {L}, {P} càng hiểu rằng {A} là điều không thể né tránh.",
    "Mỗi khi nhắc đến {O}, giọng {P} lại chùng xuống.",
    "{P2} mỉm cười, bảo rằng {A} rồi cũng sẽ có lúc tìm được chỗ đứng của nó.",
    "Chuyện về {O} lan đi khắp {L} chỉ sau một đêm.",
    "Có lúc {P} muốn bỏ lại tất cả, nhưng hình ảnh {O} cứ quay về trong trí nhớ.",
    "Khi {W} phủ xuống, {L} chìm vào một vẻ tĩnh lặng khó tả.",
    "\"{Q},\" {P2} đáp, giọng nhẹ như không.",
    "{P} chợt hiểu vì sao {P2} luôn giữ {O} bên mình.",
    "Quanh {L}, người ta vẫn kể nhau nghe về {A} theo cách riêng của mình.",
]
NARR_TITLE = [
    "Ký ức {L}", "Bí mật của {O}", "Hành trình đi tìm {A}", "{L} và {A}",
    "Lời nhắn từ {L}", "Câu chuyện về {O}", "{P} và {O}", "Dấu chân quanh {L}",
]
NARR_CH_TITLE = [
    "{L}", "Chuyện về {O}", "Khi {A} trở lại", "Lời hứa ở {L}",
    "{A}", "Người trở về {L}", "Trước khi {O} biến mất", "Đêm ở {L}",
    "Tiếng vọng của {A}", "{P} và {P2}", "Phía sau {O}",
]
NARR_DESC = [
    "Cuốn sách kể về {P} và hành trình đi tìm {A} giữa {L}.",
    "Từ {O}, câu chuyện mở ra những lớp ký ức về {A}.",
    "Một tác phẩm giàu cảm xúc, nơi {L} trở thành chứng nhân của {A}.",
]

EXPOSITORY = {
    "Khoa học": dict(
        D=["vật lý hiện đại", "sinh học tế bào", "khoa học khí hậu", "thiên văn học", "hóa học vật liệu"],
        A=["năng lượng", "cân bằng sinh thái", "quy luật tự nhiên", "phương pháp thực nghiệm", "dữ liệu quan sát", "mô hình dự báo", "tính lặp lại của thí nghiệm"],
        M=["thiết kế thí nghiệm có nhóm đối chứng", "đo đạc lặp lại nhiều lần", "xây dựng mô hình toán học", "đối chiếu với số liệu thực địa"],
        R=["sai số nhỏ hơn", "kết luận đáng tin cậy hơn", "dự báo sát thực tế hơn", "kết quả dễ kiểm chứng hơn"],
        S=["điều kiện môi trường thay đổi", "mẫu thử được lấy từ nhiều địa điểm", "thiết bị đo được hiệu chuẩn lại"],
    ),
    "Công nghệ": dict(
        D=["phát triển phần mềm", "hệ thống phân tán", "an toàn thông tin", "trí tuệ nhân tạo", "điện toán đám mây"],
        A=["kiến trúc hệ thống", "khả năng mở rộng", "độ trễ", "tính sẵn sàng", "dữ liệu huấn luyện", "chuẩn giao tiếp", "bộ nhớ đệm"],
        M=["chia nhỏ hệ thống thành các dịch vụ độc lập", "kiểm thử tự động ở từng tầng", "lưu tạm dữ liệu truy cập thường xuyên", "giám sát liên tục các chỉ số vận hành"],
        R=["độ trễ giảm đáng kể", "hệ thống ổn định hơn", "chi phí vận hành thấp hơn", "lỗi được phát hiện sớm hơn"],
        S=["lượng truy cập tăng đột biến", "một thành phần của hệ thống gặp sự cố", "đội ngũ cần phát hành phiên bản mới"],
    ),
    "Kinh tế": dict(
        D=["kinh tế vi mô", "quản trị doanh nghiệp", "thị trường tài chính", "thương mại quốc tế", "khởi nghiệp"],
        A=["cung và cầu", "dòng tiền", "chi phí cơ hội", "lợi thế cạnh tranh", "rủi ro đầu tư", "lạm phát", "năng suất lao động"],
        M=["lập kế hoạch ngân sách theo từng quý", "đa dạng hóa danh mục đầu tư", "phân tích điểm hòa vốn", "theo dõi chỉ số tài chính định kỳ"],
        R=["chi phí được kiểm soát tốt hơn", "lợi nhuận ổn định hơn", "rủi ro phân tán hơn", "quyết định có cơ sở hơn"],
        S=["giá nguyên liệu biến động", "nhu cầu thị trường suy giảm", "doanh nghiệp mở rộng sang thị trường mới"],
    ),
    "Tâm lý - Kỹ năng": dict(
        D=["tâm lý học hành vi", "phát triển bản thân", "quản lý thời gian", "giao tiếp hằng ngày", "làm việc nhóm"],
        A=["thói quen", "động lực nội tại", "sự tập trung", "cảm xúc", "khả năng lắng nghe", "mục tiêu cá nhân", "giấc ngủ"],
        M=["chia mục tiêu lớn thành bước nhỏ", "ghi chép lại những gì đã làm mỗi ngày", "dành thời gian nghỉ ngơi có chủ đích", "đặt câu hỏi mở khi trò chuyện"],
        R=["tinh thần thoải mái hơn", "hiệu quả công việc tăng lên", "các mối quan hệ gắn kết hơn", "áp lực giảm đi rõ rệt"],
        S=["khối lượng công việc dồn lại", "hai người có quan điểm trái ngược", "ta bắt đầu một thói quen mới"],
    ),
}
EXPO_TPL = [
    "Trong {D}, {A} đóng vai trò then chốt đối với {B}.",
    "Một cách tiếp cận phổ biến là {M}, nhờ đó {R}.",
    "Ví dụ, khi {S}, người ta thường nhận thấy {R}.",
    "Nhiều nghiên cứu cho thấy {A} có quan hệ chặt chẽ với {B}.",
    "Để hiểu rõ {A}, trước hết cần xem xét {B} trong bối cảnh {D}.",
    "Tuy nhiên, {A} không phải lúc nào cũng dẫn đến {R}.",
    "Điều này giải thích vì sao {M} được áp dụng rộng rãi trong {D}.",
    "Khi {S}, việc {M} giúp {R}.",
    "Đây là nền tảng để tiếp tục tìm hiểu {B} ở các phần sau.",
    "Sai lầm thường gặp là bỏ qua {A}, khiến việc {M} kém hiệu quả.",
    "Trong thực tế, {S} là lúc {A} bộc lộ rõ nhất.",
]
EXPO_TITLE = [
    "Nhập môn {D}", "{A}: từ nguyên lý đến thực hành", "Cẩm nang {D}",
    "Hiểu về {A}", "{D} cho người bắt đầu", "Những điều cần biết về {A}",
]
EXPO_CH_TITLE = [
    "Nền tảng của {A}", "{A} và {B}", "{M}", "Thực hành: {M}",
    "Những sai lầm thường gặp về {A}", "{D} trong thực tế", "Tổng quan về {D}",
    "Khi {S}", "Đo lường {A}", "Từ {A} đến {B}",
]
EXPO_DESC = [
    "Cuốn sách giới thiệu {A} trong lĩnh vực {D}, kèm các cách tiếp cận thực hành.",
    "Từ {A} đến {B}, tác giả dẫn dắt người đọc qua những ví dụ gần gũi của {D}.",
    "Một tài liệu tham khảo cô đọng về {D}, tập trung vào {A} và {B}.",
]

SECTION_HEADINGS = ["Bối cảnh", "Diễn biến", "Điểm nhấn", "Dư âm", "Ghi chép thêm", "Tóm lược", "Câu hỏi mở"]

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
DEM = ["Văn", "Thị", "Minh", "Quốc", "Thanh", "Hữu", "Ngọc", "Gia", "Anh", "Đức", "Thu", "Hải", "Bảo", "Tuấn"]
TEN = ["An", "Bình", "Chi", "Dung", "Giang", "Hà", "Hiếu", "Khoa", "Lan", "Linh", "Long", "Mai", "Nam",
       "Phúc", "Quân", "Thảo", "Trang", "Tú", "Việt", "Yến", "Đạt", "Sơn", "Vy", "Khánh", "Hòa", "Lâm"]

CATEGORIES = list(NARRATIVE) + list(EXPOSITORY)


# ---------------------------------------------------------------- bộ sinh nội dung

def cap(s: str) -> str:
    return s[:1].upper() + s[1:]


class BookWriter:
    """Sinh văn bản cho một sách; có 'dàn nhân vật' riêng để các chương nhất quán."""

    def __init__(self, category: str, rng: random.Random):
        self.category = category
        self.rng = rng
        self.narrative = category in NARRATIVE
        self.pools = NARRATIVE[category] if self.narrative else EXPOSITORY[category]
        self.cast = {k: rng.sample(v, min(3, len(v))) for k, v in self.pools.items()}
        self.tpl = NARR_TPL if self.narrative else EXPO_TPL
        self._last = -1

    def pick(self, slot: str, avoid: str | None = None) -> str:
        pool = self.pools[slot]
        for _ in range(8):
            v = self.rng.choice(self.cast[slot]) if self.rng.random() < 0.75 else self.rng.choice(pool)
            if v != avoid:
                return v
        return v

    def fill(self, template: str) -> str:
        r = self.rng
        v = {}
        if self.narrative:
            v["P"] = self.pick("P")
            v["P2"] = self.pick("P", avoid=v["P"])
            v["L"], v["O"], v["A"] = self.pick("L"), self.pick("O"), self.pick("A")
            v["V"], v["T"], v["W"], v["Q"] = r.choice(NARR_V), r.choice(NARR_T), r.choice(NARR_W), r.choice(NARR_Q)
        else:
            v["D"] = self.pick("D")
            v["A"] = self.pick("A")
            v["B"] = self.pick("A", avoid=v["A"])
            v["M"], v["R"], v["S"] = self.pick("M"), self.pick("R"), self.pick("S")
        return template.format(**v)

    def sentence(self) -> str:
        idx = self.rng.randrange(len(self.tpl))
        while idx == self._last:
            idx = self.rng.randrange(len(self.tpl))
        self._last = idx
        return cap(self.fill(self.tpl[idx]))

    def paragraph(self) -> str:
        return " ".join(self.sentence() for _ in range(self.rng.randint(4, 6)))

    def chapter_content(self) -> str:
        # 12–18 đoạn ≈ 6–9 nghìn ký tự: đủ dài để E-Reader chia thành nhiều trang
        return "\n\n".join(self.paragraph() for _ in range(self.rng.randint(12, 18)))

    def sections(self) -> list[dict]:
        heads = self.rng.sample(SECTION_HEADINGS, self.rng.randint(2, 4))
        return [
            {
                "sectionNo": n,
                "heading": h,
                "text": " ".join(self.sentence() for _ in range(self.rng.randint(2, 3))),
            }
            for n, h in enumerate(heads, start=1)
        ]

    def unique(self, templates: list[str], seen: set[str]) -> str:
        for _ in range(30):
            t = cap(self.fill(self.rng.choice(templates)))
            if t not in seen:
                seen.add(t)
                return t
        t = f"{t} (tiếp)"
        seen.add(t)
        return t

    def description(self) -> str:
        return cap(self.fill(self.rng.choice(NARR_DESC if self.narrative else EXPO_DESC)))


def make_book(index: int, seed: int, used_titles: set[str], now: datetime) -> dict:
    rng = random.Random(f"{seed}-book-{index}")
    category = CATEGORIES[index % len(CATEGORIES)]
    w = BookWriter(category, rng)

    title_tpls = NARR_TITLE if w.narrative else EXPO_TITLE
    title = w.unique(title_tpls, used_titles)

    categories = [category]
    if rng.random() < 0.3:
        extra = rng.choice([c for c in CATEGORIES if c != category])
        categories.append(extra)

    chapter_titles: set[str] = set()
    ch_tpls = NARR_CH_TITLE if w.narrative else EXPO_CH_TITLE
    chapters = [
        {
            "chapterNo": n,
            "title": w.unique(ch_tpls, chapter_titles),
            "content": w.chapter_content(),
            "sections": w.sections(),
        }
        for n in range(1, rng.randint(5, 10) + 1)
    ]

    created = now - timedelta(days=rng.randint(1, 120), minutes=rng.randint(0, 1439))
    created = created.replace(microsecond=0)  # BSON date chính xác đến mili-giây
    return {
        "_id": ObjectId(f"{ID_PREFIX}{index:020x}"),
        "title": title,
        "author": f"{rng.choice(HO)} {rng.choice(DEM)} {rng.choice(TEN)}",
        "categories": categories,
        "description": w.description(),
        "coverUrl": f"https://picsum.photos/seed/dl-book-{index}/300/450",
        "chapters": chapters,
        "createdAt": created,
        "updatedAt": created,
    }


# ---------------------------------------------------------------- kiểm tra theo schema

def _bson_type(v) -> str:
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int" if -(2**31) <= v < 2**31 else "long"
    return {str: "string", float: "double", datetime: "date", list: "array",
            dict: "object", ObjectId: "objectId", type(None): "null"}.get(type(v), type(v).__name__)


def check(value, schema: dict, path: str, errors: list[str]) -> None:
    """Bộ kiểm tra tối giản cho phần $jsonSchema mà books.schema.json sử dụng."""
    want = schema.get("bsonType")
    if want:
        want = want if isinstance(want, list) else [want]
        got = _bson_type(value)
        if got not in want:
            errors.append(f"{path}: cần {want}, có {got}")
            return
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: ngắn hơn minLength")
        if len(value) > schema.get("maxLength", 10**9):
            errors.append(f"{path}: dài quá maxLength {schema['maxLength']}")
    if isinstance(value, int) and not isinstance(value, bool) and value < schema.get("minimum", -(10**18)):
        errors.append(f"{path}: nhỏ hơn minimum")
    if isinstance(value, list):
        if len(value) > schema.get("maxItems", 10**9):
            errors.append(f"{path}: vượt maxItems")
        if schema.get("uniqueItems") and len({json.dumps(x, default=str) for x in value}) != len(value):
            errors.append(f"{path}: phần tử trùng")
        for i, item in enumerate(value):
            if "items" in schema:
                check(item, schema["items"], f"{path}[{i}]", errors)
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: thiếu trường {req}")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                check(value[key], sub, f"{path}.{key}", errors)


def validate_all(books: list[dict], schema: dict) -> list[str]:
    errors: list[str] = []
    for b in books:
        check(b, schema["$jsonSchema"], f"book[{b['_id']}]", errors)
        nums = [c["chapterNo"] for c in b["chapters"]]
        if nums != list(range(1, len(nums) + 1)):
            errors.append(f"book[{b['_id']}]: chapterNo không liên tục từ 1")
    return errors


# ---------------------------------------------------------------- ghi MongoDB

def write_mongo(books: list[dict], schema: dict, uri: str, reset: bool, apply_validator: bool) -> None:
    from pymongo import MongoClient, ReplaceOne
    from pymongo.errors import PyMongoError

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except PyMongoError as ex:
        sys.exit(f"Không kết nối được MongoDB ({ex.__class__.__name__}). "
                 "Đã chạy `docker compose up -d` chưa? Xem mục xử lý lỗi cổng 27017 trong docs/SHARED.md.")
    db = client.get_default_database(default="digital_library")
    name = "books"

    if apply_validator:  # cùng validator với backend (CatalogMongoInitializer), chạy lặp an toàn
        if name not in db.list_collection_names():
            db.create_collection(name)
        db.command({"collMod": name, "validator": schema, "validationLevel": "strict", "validationAction": "error"})

    col = db[name]
    first_id = ObjectId(f"{ID_PREFIX}{0:020x}")
    last_id = ObjectId(f"{ID_PREFIX}{(1 << 80) - 1:020x}")
    if reset:
        deleted = col.delete_many({"_id": {"$gte": first_id, "$lte": last_id}}).deleted_count
        print(f"Đã xóa {deleted} sách seed cũ.")

    ops = [ReplaceOne({"_id": b["_id"]}, b, upsert=True) for b in books]
    for i in range(0, len(ops), 20):
        col.bulk_write(ops[i:i + 20], ordered=False)

    # Index (text, categories, createdAt) do backend tạo khi khởi động (CatalogMongoInitializer);
    # script không tạo để tránh xung đột định nghĩa index với Spring Data.

    print(f"Collection {db.name}.{name} hiện có {col.count_documents({})} sách "
          f"({col.count_documents({'_id': {'$gte': first_id, '$lte': last_id}})} sách seed).")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--count", type=int, default=60, help="số đầu sách (barem: 50–100), mặc định 60")
    ap.add_argument("--seed", type=int, default=2026, help="hạt giống ngẫu nhiên, cùng seed → cùng dữ liệu")
    ap.add_argument("--uri", default=os.environ.get("MONGO_URI", DEFAULT_URI), help="MongoDB URI (mặc định lấy MONGO_URI)")
    ap.add_argument("--reset", action="store_true", help="xóa các sách seed cũ trước khi nạp")
    ap.add_argument("--dry-run", action="store_true", help="chỉ sinh và kiểm tra schema, không ghi DB")
    ap.add_argument("--skip-validator", action="store_true", help="không áp validator (backend vẫn tự áp khi chạy)")
    ap.add_argument("--ids-out", default=str(IDS_PATH), help="file JSON chứa bookId cho Đạt seed Redis")
    args = ap.parse_args()

    if not 1 <= args.count <= 1000:
        sys.exit("--count phải trong khoảng 1–1000")
    if args.count < 50 or args.count > 100:
        print(f"Lưu ý: barem yêu cầu 50–100 đầu sách, bạn đang chọn {args.count}.")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)  # ổn định trong ngày
    used: set[str] = set()
    books = [make_book(i + 1, args.seed, used, now) for i in range(args.count)]

    errors = validate_all(books, schema)
    if errors:
        sys.exit("Dữ liệu sinh ra vi phạm schema:\n  " + "\n  ".join(errors[:20]))

    n_ch = sum(len(b["chapters"]) for b in books)
    chars = sum(len(c["content"]) for b in books for c in b["chapters"])
    print(f"Đã sinh {len(books)} sách, {n_ch} chương, {chars / 1e6:.2f} triệu ký tự; "
          f"chương/sách {min(len(b['chapters']) for b in books)}–{max(len(b['chapters']) for b in books)}; "
          "kiểm tra schema: OK")

    if args.dry_run:
        print("--dry-run: không ghi MongoDB và không ghi file ID.")
        return

    write_mongo(books, schema, args.uri, args.reset, not args.skip_validator)

    ids = [{"bookId": str(b["_id"]), "title": b["title"], "chapterCount": len(b["chapters"])} for b in books]
    Path(args.ids_out).write_text(json.dumps(ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã ghi {len(ids)} bookId vào {args.ids_out} (Đạt dùng để seed Redis).")


if __name__ == "__main__":
    main()
