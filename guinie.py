"""质量门禁 —— 道统算子谱（guinie）
道统出处：立圭为准，奉为圭臬
工程映射：L0检查与发布前门禁的统一标尺
生长纪律：本地生长自由，推送远端需治理决议发令。
"""
import re

class Gate:
    """质量门禁：规则登记 + 逐条执行 + 报告聚合（规则即 callable(target)）。"""

    def __init__(self, rules=None):
        self.rules = dict(rules or {})       # {规则名: callable(target) -> (ok, 说明)}

    def describe(self) -> dict:
        return {"name": "guinie", "role": "L0检查与发布前门禁的统一标尺",
                "stage": "m1", "rules": len(self.rules)}

    def register(self, name, rule):
        """登记一条门禁规则；重名即拒绝，规则表只增不覆盖。"""
        if name in self.rules:
            raise ValueError(f"规则 {name} 已登记，重名拒绝（只增不覆盖）")
        if not callable(rule):
            raise TypeError(f"规则 {name} 必须为 callable(target)")
        self.rules[name] = rule

    def run_all(self, target):
        """逐条执行规则，返回报告：{"passed": [...], "failed": [...], "ok": bool}。"""
        passed, failed = [], []
        for name, rule in self.rules.items():
            try:
                ok, note = rule(target)
            except Exception as exc:                     # 规则自身崩坏视同失败
                ok, note = False, f"规则执行异常：{type(exc).__name__}: {exc}"
            ok = bool(ok)
            (passed if ok else failed).append({"rule": name, "ok": ok, "note": str(note)})
        return {"passed": passed, "failed": failed, "ok": not failed}

    @staticmethod
    def version_monotonic(old, new):
        """内置规则：语义化版本单调不减，回退即不通过（落实只增不覆盖）。

        解析失败同样不通过；非负整数段逐位比较，等版与升版皆放行。
        """
        def parse(v):
            if not isinstance(v, str):
                return None
            s = v.strip()
            if not s or not re.fullmatch(r"(0|[1-9]\d*)(?:\.(0|[1-9]\d*))*", s):
                return None
            return [int(p) for p in s.split(".")]

        a, b = parse(old), parse(new)
        if a is None or b is None:
            return False, f"版本不可解析：old={old!r} new={new!r}"
        if b >= a:
            return True, f"{old} -> {new} 单调不回退"
        return False, f"版本回退：{old} -> {new}（只增不覆盖被违）"
