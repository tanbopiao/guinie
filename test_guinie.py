import unittest
from guinie import Gate

class T(unittest.TestCase):
    def test_all_green_report(self):
        g = Gate()
        g.register("非空", lambda t: (bool(t), "非空检查"))
        g.register("长度", lambda t: (len(t) >= 2, f"len={len(t)}"))
        r = g.run_all("玄圭")
        self.assertTrue(r["ok"])
        self.assertEqual(len(r["passed"]), 2)
        self.assertEqual(r["failed"], [])

    def test_failed_rule_goes_to_failed(self):
        g = Gate()
        g.register("恒假", lambda t: (False, "此路不通"))
        g.register("恒真", lambda t: (True, "放行"))
        r = g.run_all(object())
        self.assertFalse(r["ok"])
        self.assertEqual([f["rule"] for f in r["failed"]], ["恒假"])
        self.assertEqual([p["rule"] for p in r["passed"]], ["恒真"])

    def test_version_regression_rejected(self):
        self.assertFalse(Gate.version_monotonic("1.2.3", "1.2.2")[0])
        self.assertTrue(Gate.version_monotonic("1.2.3", "1.2.4")[0])
        self.assertTrue(Gate.version_monotonic("1.2", "1.2.1")[0])
        self.assertFalse(Gate.version_monotonic("1.02", "1.2")[0])   # 非法版本不可解析
        self.assertFalse(Gate.version_monotonic("1.0", None)[0])

    def test_empty_ruleset_trivially_passes(self):
        g = Gate()
        r = g.run_all("anything")
        self.assertTrue(r["ok"])
        self.assertEqual(r["passed"], [])
        self.assertEqual(r["failed"], [])

    def test_rule_exception_counts_as_failed(self):
        g = Gate()
        g.register("炸裂", lambda t: 1 / 0)
        r = g.run_all(None)
        self.assertFalse(r["ok"])
        self.assertIn("ZeroDivisionError", r["failed"][0]["note"])

    def test_duplicate_register_rejected(self):
        g = Gate()
        g.register("同规", lambda t: (True, ""))
        with self.assertRaises(ValueError):
            g.register("同规", lambda t: (False, ""))

if __name__ == "__main__":
    unittest.main()
