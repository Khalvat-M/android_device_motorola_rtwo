#!/usr/bin/env python3
"""Merge carriers/*.xml into the Motorola vendor.xml -> rro/res/xml/vendor.xml

  gen_carrier_config.py          regenerate output
  gen_carrier_config.py --check  exit 1 if output is stale (used by the .mk)

A snippet is matched to an existing <carrier_config> by its attributes
(mcc, mnc, imsi, spn, gid1, ...). Matching block: keys are merged (ours win).
No match: the block is appended at the end of the list.
"""
import os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
# adjust if your tree differs
MOTO = os.environ.get("MOTO_VENDOR_XML", os.path.join(
    HERE, "../../../../../../vendor/motorola/rtwo/rro_overlays/CarrierConfigOverlay/res/xml/vendor.xml"))
OUT = os.path.join(HERE, "rro/res/xml/vendor.xml")

BLOCK = re.compile(r'[ \t]*<carrier_config(?P<attrs>(?:\s+[\w:-]+="[^"]*")*)\s*'
                   r'(?:/>|>(?P<body>.*?)</carrier_config>)[ \t]*\n?', re.S)
ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
KEY = re.compile(r'<(?:boolean|int|long|string|int-array|string-array|long-array|boolean-array|pbundle_as_map)\s+name="([^"]+)"')
ELEM = re.compile(r'[ \t]*<(?P<t>boolean|int|long|string|int-array|string-array|long-array|boolean-array)\s+name="(?P<n>[^"]+)"'
                  r'(?:[^>]*?/>|[^>]*?>.*?</(?P=t)>)[ \t]*\n?', re.S)

def attrs(a): return dict(ATTR.findall(a or ""))

def merge_body(old_body, new_body):
    names = set(m.group("n") for m in ELEM.finditer(new_body))
    kept = ELEM.sub(lambda m: "" if m.group("n") in names else m.group(0), old_body or "")
    kept = kept.strip("\n")
    new = new_body.strip("\n")
    return (kept + "\n" if kept.strip() else "") + new + "\n"

def fmt(a, body):
    at = "".join(f' {k}="{v}"' for k, v in a.items())
    return f"    <carrier_config{at}>\n{body}    </carrier_config>\n"

def build():
    text = open(MOTO, encoding="utf-8").read()
    for f in sorted(glob.glob(os.path.join(HERE, "carriers", "*.xml"))):
        snip = open(f, encoding="utf-8").read()
        snip = re.sub(r"<!--.*?-->", "", snip, flags=re.S)
        m = BLOCK.search(snip)
        if not m: sys.exit(f"{f}: no <carrier_config> found")
        a, body = attrs(m.group("attrs")), (m.group("body") or "")
        body = "\n".join(l for l in body.splitlines() if l.strip()) + "\n"
        hit = None
        for b in BLOCK.finditer(text):
            if attrs(b.group("attrs")) == a: hit = b; break
        if hit:
            text = text[:hit.start()] + fmt(a, merge_body(hit.group("body"), body)) + text[hit.end():]
            print(f"merged  {os.path.basename(f)}", file=sys.stderr)
        else:
            i = text.rindex("</carrier_config_list>")
            text = text[:i] + fmt(a, body) + text[i:]
            print(f"appended {os.path.basename(f)}", file=sys.stderr)
    return text

if __name__ == "__main__":
    out = build()
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        sys.exit(0 if cur == out else 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(out)
