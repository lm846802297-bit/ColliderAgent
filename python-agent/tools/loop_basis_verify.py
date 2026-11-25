"""Independent exact gate for rational or one-quadratic dlog basis proposals."""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import re
from pathlib import Path

import sympy as sp

MAX_BYTES = 32_000_000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def loads(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError("input exceeds size limit")
    return json.loads(raw, object_pairs_hook=json_object)


def read(path):
    with Path(path).open("rb") as stream:
        return stream.read(MAX_BYTES + 1)


def keys(obj, required, optional=()):
    if not isinstance(obj, dict) or not set(required) <= obj.keys() <= set(required) | set(optional):
        raise ValueError(f"expected fields {list(required)}, optional {list(optional)}")


def symbol(name):
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", name):
        raise ValueError("invalid symbol name")
    return sp.Symbol(name)


def expression(value, names):
    """Small data-only grammar: integers, symbols, + - * / and integer **."""
    if type(value) is int:
        return sp.Integer(value)
    if not isinstance(value, str) or len(value) > 200_000:
        raise ValueError("expected bounded exact expression string or integer")

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return sp.Integer(node.value)
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            arg = visit(node.operand)
            return -arg if isinstance(node.op, ast.USub) else arg
        if isinstance(node, ast.BinOp):
            lhs, rhs = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return lhs + rhs
            if isinstance(node.op, ast.Sub):
                return lhs - rhs
            if isinstance(node.op, ast.Mult):
                return lhs * rhs
            if isinstance(node.op, ast.Div) and rhs != 0:
                return lhs / rhs
            if isinstance(node.op, ast.Pow) and rhs.is_Integer and abs(rhs) <= 128:
                if lhs != 0 or rhs >= 0:
                    return lhs ** rhs
        raise ValueError("expression outside exact arithmetic grammar")

    return visit(ast.parse(value.strip(), mode="eval").body)


class Field:
    def __init__(self, variables, epsilon, root_spec=None):
        self.variables = tuple(variables)
        self.epsilon = epsilon
        self.names = {str(x): x for x in (*variables, epsilon)}
        self.domain = sp.QQ.frac_field(*variables, epsilon)
        self.root = self.radicand = None
        if root_spec is not None:
            keys(root_spec, ("name", "radicand"))
            r = symbol(root_spec["name"])
            if str(r) in self.names:
                raise ValueError("root collides with another generator")
            d = expression(root_spec["radicand"], {str(x): x for x in variables})
            d = self.rational(d)
            num, den = d.as_numer_denom()
            factors = [sp.factor_list(p, *variables) for p in (num, den)]
            c = factors[0][0] / factors[1][0]
            if not d or (all(k % 2 == 0 for _, fs in factors for _, k in fs)
                         and sp.sqrt(c).is_Rational):
                raise ValueError("radicand must be nonzero and nonsquare")
            self.root, self.radicand = r, d
            self.names[str(r)] = r
            self.modulus = sp.Poly(r*r-d, r, domain=self.domain)

    def rational(self, x):
        return self.domain.to_sympy(self.domain.from_sympy(sp.cancel(x)))

    def normal(self, x):
        if not x:
            return sp.S.Zero
        if self.root is None or not x.has(self.root):
            return self.rational(x)
        r = self.root
        num, den = sp.cancel(x).as_numer_denom()
        n = sp.Poly(num, r, domain=self.domain).rem(self.modulus)
        d = sp.Poly(den, r, domain=self.domain).rem(self.modulus)
        if d.is_zero:
            raise ValueError("denominator vanishes in the quadratic field")
        return (n * d.invert(self.modulus)).rem(self.modulus).as_expr()

    def parse(self, x):
        v = expression(x, self.names)
        if not self.root:
            return self.normal(v)
        # Validate intermediate divisions too (cancelled syntactic factors can otherwise
        # hide a zero denominator modulo the defining quadratic relation).
        def parse_node(node):
            if isinstance(node, ast.BinOp):
                a, b = parse_node(node.left), parse_node(node.right)
                op = node.op
                if isinstance(op, ast.Div):
                    if not b:
                        raise ValueError("division by zero in the quadratic field")
                    return self.normal(a / b)
                if isinstance(op, ast.Pow):
                    if not b.is_Integer or abs(b) > 128 or (not a and b < 0):
                        raise ValueError("invalid integer power")
                    return self.normal(a ** b)
                for cls, f in ((ast.Add, lambda: a+b), (ast.Sub, lambda: a-b),
                               (ast.Mult, lambda: a*b)):
                    if isinstance(op, cls):
                        return self.normal(f())
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                arg = parse_node(node.operand)
                return -arg if isinstance(node.op, ast.USub) else arg
            return expression(ast.unparse(node), self.names)
        return parse_node(ast.parse(x.strip(), mode="eval").body) if isinstance(x, str) else v

    def derivative(self, a, x):
        result = sp.diff(a, x)
        if self.root and a.has(self.root):
            result += sp.diff(a, self.root)*sp.diff(self.radicand, x)/(2*self.root)
        return self.normal(result)


def matrix(entries, n, parser):
    """Sparse triples (zero-based coordinates); omitted entries are zero."""
    if not isinstance(entries, list) or len(entries) > n*n:
        raise ValueError("matrix requires sparse entry list")
    values = {}
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 3:
            raise ValueError("invalid matrix entry")
        i, j, v = entry
        if any(type(k) is not int or not 0 <= k < n for k in (i, j)):
            raise ValueError("invalid matrix index")
        if (i, j) in values:
            raise ValueError("duplicate matrix entry")
        values[i, j] = parser(v)
    return sp.SparseMatrix(n, n, values)


def first_nonzero(m, field):
    for (i, j), value in sorted(m.todok().items()):
        check = field.normal(value)
        if check != 0:
            return {"row": i, "column": j, "residual": str(check)[:2000]}
    return None


def prepare(src):
    keys(src, ("schema", "masters", "variables", "epsilon", "connections", "letters"),
         ("quadratic_root",))
    if src["schema"] != "pheno-loop-source-v1":
        raise ValueError("unknown source schema")
    masters, variables = src["masters"], src["variables"]
    if not isinstance(masters, list) or not 1 <= len(masters) <= 256 or not all(
        isinstance(x, str) and x.strip() and len(x) <= 1024 for x in masters
    ) or len(set(masters)) != len(masters):
        raise ValueError("invalid ordered master list")
    if not isinstance(variables, list) or not 1 <= len(variables) <= 16:
        raise ValueError("invalid variable list")
    xs, eps = [symbol(x) for x in variables], symbol(src["epsilon"])
    if len(set((*xs, eps))) != len(xs)+1:
        raise ValueError("duplicate variables or regulator")
    f = Field(xs, eps, src.get("quadratic_root"))
    keys(src["connections"], variables)
    n = len(masters)
    a = [matrix(src["connections"][str(x)], n, f.parse) for x in xs]
    if not isinstance(src["letters"], dict) or not 1 <= len(src["letters"]) <= 128:
        raise ValueError("invalid frozen alphabet")
    letters = {}
    for label, value in src["letters"].items():
        symbol(label)
        v = f.parse(value)
        if not v or v.has(eps) or not any(f.derivative(v, x) for x in xs):
            raise ValueError("letter must be nonzero, kinematic and regulator-independent")
        letters[label] = [f.normal(f.derivative(v, x)/v) for x in xs]
    return n, xs, eps, f, a, letters


def verify(source_bytes, proposal_bytes):
    identity = digest(source_bytes)
    def receipt(status, reason, **kw):
        return dict(status=status, reason=reason, source_sha256=identity,
                    proposal_sha256=digest(proposal_bytes), **kw)

    try:
        p = loads(proposal_bytes)
        keys(p, ("schema", "source_sha256", "transform", "inverse", "residues"))
        if p["schema"] != "pheno-loop-proposal-v1" or p["source_sha256"] != identity:
            return receipt("REJECT", "source-or-schema-mismatch")
        n, xs, eps, f, aa, ll = prepare(loads(source_bytes))
        t, u = (matrix(p[k], n, f.parse) for k in ("transform", "inverse"))
        failure = first_nonzero(t*u-sp.eye(n), f)
        if failure:
            return receipt("REJECT", "invalid-inverse", **failure)
        keys(p["residues"], (), ll)
        rs = {k: matrix(v, n, lambda x: expression(x, {})) for k,v in p["residues"].items()}
        ds = [sp.SparseMatrix(n,n,{ij:f.derivative(val, x) for ij,val in t.todok().items()})
              for x in xs]
        bs = []
        for j, (x, a, dt) in enumerate(zip(xs, aa, ds)):
            b = sp.zeros(n, n, cls=sp.SparseMatrix)
            for k, r in rs.items():
                b += r*(eps*ll[k][j])
            # Since T U = 1 in a field, dT+TA = BT is equivalent to
            # the independently reconstructed (dT+TA)U = B, without expression swell.
            failure = first_nonzero(dt+t*a-b*t, f)
            if failure:
                return receipt("REJECT", "connection-identity", direction=str(x), **failure)
            bs.append(b)
        # The exterior derivative of each dlog vanishes locally. Hence
        # flatness of the proven target is exactly pairwise vanishing of commutators.
        for i, j in itertools.combinations(range(len(xs)), 2):
            failure = first_nonzero(bs[i]*bs[j]-bs[j]*bs[i], f)
            if failure:
                return receipt("REJECT", "nonflat-connection", directions=[str(xs[i]), str(xs[j])],
                               **failure)
        return receipt("PASS", "generic-exact-dlog", masters=n, directions=list(map(str,xs)))
    except (ValueError, TypeError, SyntaxError, ArithmeticError, RecursionError,
            sp.PolynomialError, sp.polys.polyerrors.BasePolynomialError) as exc:
        return receipt("REJECT", "invalid-input", detail=str(exc)[:2000])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("proposal")
    args = parser.parse_args()
    v = verify(read(args.source), read(args.proposal))
    print(json.dumps(v, sort_keys=True))
    return 0 if v["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
