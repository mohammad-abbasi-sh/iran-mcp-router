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


if __name__ == "__main__":
    unittest.main()
