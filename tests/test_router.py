"""Real tests for the iran-mcp-router engine (stdlib unittest, no deps)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from router import normalize_fa, route  # noqa: E402


class TestNormalizeFa(unittest.TestCase):
    def test_arabic_yeh_kaf(self):
        self.assertEqual(normalize_fa("مي‌خوام"), "میخوام")

    def test_arabic_kaf(self):
        self.assertEqual(normalize_fa("كتاب"), "کتاب")

    def test_persian_digits(self):
        self.assertEqual(normalize_fa("۱۲۳"), "123")

    def test_arabic_indic_digits(self):
        self.assertEqual(normalize_fa("٤٥٦"), "456")

    def test_zwnj_removed(self):
        self.assertEqual(normalize_fa("می‌خواهم"), "میخواهم")

    def test_whitespace_collapsed(self):
        self.assertEqual(normalize_fa("  قیمت   سکه  "), "قیمت سکه")

    def test_casefold(self):
        self.assertEqual(normalize_fa("Dollar Price"), "dollar price")

    def test_empty(self):
        self.assertEqual(normalize_fa(""), "")


class TestRoutePersian(unittest.TestCase):
    def test_coin_price(self):
        top = route("قیمت سکه امامی")[0]
        self.assertEqual(top["server_id"], "tgju-mcp")
        self.assertEqual(top["suggested_tool"], "tj_get_prices")

    def test_flight_tehran_mashhad(self):
        top = route("بلیط هواپیما تهران مشهد")[0]
        self.assertIn(top["server_id"], ("mrbilit-mcp", "alibaba-ir-mcp"))
        if top["server_id"] == "mrbilit-mcp":
            self.assertEqual(top["suggested_tool"], "mb_search_flights")

    def test_stock_index(self):
        top = route("شاخص بورس تهران")[0]
        self.assertEqual(top["server_id"], "tsetmc-mcp")

    def test_phone_price(self):
        top = route("قیمت گوشی سامسونگ")[0]
        self.assertEqual(top["server_id"], "torob-mcp")

    def test_doctor_appointment(self):
        top = route("نوبت دکتر قلب در تهران")[0]
        self.assertEqual(top["server_id"], "paziresh24-mcp")

    def test_cheapest_intent(self):
        top = route("ارزون ترین گوشی شیائومی")[0]
        self.assertEqual(top["server_id"], "torob-mcp")
        self.assertEqual(top["suggested_tool"], "tb_cheapest")

    def test_results_have_install_and_reason(self):
        for r in route("قیمت دلار امروز"):
            self.assertTrue(r["install"].startswith("uvx "))
            self.assertTrue(r["repo"].startswith("https://github.com/"))
            self.assertTrue(r["reason"])
            self.assertGreater(r["score"], 0)


class TestRouteEnglish(unittest.TestCase):
    def test_dollar_price(self):
        self.assertEqual(route("dollar price today")[0]["server_id"], "tgju-mcp")

    def test_cheapest_flight(self):
        top = route("cheapest flight from Tehran to Mashhad")[0]
        self.assertIn(top["server_id"], ("mrbilit-mcp", "alibaba-ir-mcp"))

    def test_stock_index(self):
        self.assertEqual(route("tehran stock exchange index")[0]["server_id"], "tsetmc-mcp")

    def test_order_food(self):
        self.assertEqual(route("order food online")[0]["server_id"], "snapp-mcp")


class TestDeterminism(unittest.TestCase):
    def test_same_query_same_result(self):
        a = route("قیمت سکه")
        b = route("قیمت سکه")
        self.assertEqual(a, b)

    def test_top_k_respected(self):
        self.assertLessEqual(len(route("قیمت", top_k=2)), 2)

    def test_no_match_returns_empty(self):
        self.assertEqual(route("xyzq abcdef"), [])


class TestRouteNewRules(unittest.TestCase):
    """Coverage for the 37 servers added in the full-coverage pass."""

    def _top(self, q):
        r = route(q, top_k=1)
        self.assertTrue(r, f"no result for {q!r}")
        return r[0]

    def test_audiobook(self):
        self.assertEqual(self._top("کتاب صوتی")["server_id"], "fidibo-mcp")

    def test_ebook(self):
        self.assertEqual(self._top("طاقچه کتاب الکترونیک")["server_id"], "taaghche-mcp")

    def test_villa_rental(self):
        self.assertEqual(self._top("اجاره ویلا در شمال")["server_id"], "otaghak-mcp")

    def test_car_ads(self):
        self.assertEqual(self._top("آگهی خودرو")["server_id"], "bama-ir-mcp")

    def test_inflation(self):
        top = self._top("نرخ تورم")
        self.assertEqual(top["server_id"], "amar-mcp")
        self.assertEqual(top["suggested_tool"], "am_inflation")

    def test_earthquake(self):
        self.assertEqual(self._top("زلزله امروز تهران")["server_id"], "iran-quake-mcp")

    def test_bitcoin(self):
        self.assertEqual(self._top("قیمت بیت کوین")["server_id"], "iran-crypto-mcp")

    def test_pharmacy(self):
        self.assertEqual(self._top("داروخانه آنلاین")["server_id"], "darukade-mcp")

    def test_tax(self):
        self.assertEqual(self._top("مالیات بر ارزش افزوده")["server_id"], "iran-tax-mcp")

    def test_mutual_fund(self):
        self.assertEqual(self._top("صندوق سرمایه گذاری")["server_id"], "fipiran-mcp")

    def test_software_download(self):
        self.assertEqual(self._top("دانلود نرم افزار")["server_id"], "iran-downloads-mcp")

    def test_cloud_status(self):
        self.assertEqual(self._top("وضعیت سرورهای ابری")["server_id"], "iran-cloud-status-mcp")

    def test_course(self):
        self.assertEqual(self._top("دوره آموزشی برنامه نویسی")["server_id"], "maktabkhooneh-mcp")

    def test_android_app(self):
        self.assertEqual(self._top("اپلیکیشن اندروید")["server_id"], "iran-apps-mcp")

    def test_official_gazette(self):
        self.assertEqual(self._top("روزنامه رسمی")["server_id"], "rrk-mcp")

    def test_cosmetics(self):
        self.assertEqual(self._top("لوازم آرایشی")["server_id"], "asalbanoo-mcp")

    def test_grocery(self):
        self.assertEqual(self._top("خرید سوپرمارکتی")["server_id"], "okala-mcp")

    def test_game_news(self):
        self.assertEqual(self._top("اخبار بازی")["server_id"], "gamefa-mcp")

    def test_bus_ticket(self):
        self.assertEqual(self._top("بلیط اتوبوس")["server_id"], "flytoday-mcp")

    def test_filimo_series(self):
        top = self._top("امشب توی فیلیمو چه سریالی ببینم")
        self.assertEqual(top["server_id"], "iran-vod-mcp")
        self.assertEqual(top["suggested_tool"], "vod_search")

    def test_namava_movie_en(self):
        top = self._top("where can I watch this movie, namava or filimo")
        self.assertEqual(top["server_id"], "iran-vod-mcp")

    def test_all_rules_reference_real_servers(self):
        from router import SERVER_RULES
        import json, os
        cat = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "catalog.json")))
        by_id = {s["id"]: s for s in cat["servers"]}
        for rule in SERVER_RULES:
            self.assertIn(rule["id"], by_id, f"rule for unknown server {rule['id']}")
            tools = {t["name"] for t in by_id[rule["id"]]["tools"]}
            self.assertIn(rule["tool"], tools, f"{rule['id']}: tool {rule['tool']} not in catalog")
            for intent_tool in rule.get("intent_tools", {}).values():
                self.assertIn(intent_tool, tools, f"{rule['id']}: intent tool {intent_tool} not in catalog")

    def test_full_coverage(self):
        from router import SERVER_RULES
        import json, os
        cat = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "catalog.json")))
        ruled = {r["id"] for r in SERVER_RULES}
        self.assertEqual(ruled, {s["id"] for s in cat["servers"]})


if __name__ == "__main__":
    unittest.main()
