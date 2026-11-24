"""Builds the README diagrams as light and dark SVG files. Standard library only.

    python diagrams/src/build.py
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
SKINS = {
    "light": dict(paper="#f5f5f5", ink="#2d3142", muted="#4f5d75", soft="#5a6580", line="#8a94a6",
                  accent="#bf4520", link="#2e5aa8", node="#ffffff", zone="#ececec"),
    "dark": dict(paper="#2d3142", ink="#f5f5f5", muted="#bfc0c0", soft="#b4bccb", line="#8791a6",
                 accent="#f08a59", link="#82aaea", node="#393e53", zone="#333850"),
}
SANS = "system-ui, -apple-system, 'Segoe UI', sans-serif"


class Diagram:
    def __init__(self, name, width, height, title, desc):
        self.name, self.w, self.h, self.title, self.desc = name, width, height, title, desc
        self.zones, self.arrows, self.nodes = [], [], []

    def zone(self, x, y, w, h, label):
        self.zones.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{{zone}}" stroke="{{line}}" stroke-width="1" stroke-dasharray="4 3"/>'
            f'<text x="{x + 16}" y="{y + 22}" font-size="12" font-weight="600" fill="{{soft}}">{escape(label)}</text>')

    def node(self, x, y, w, h, title, *lines, kind="step"):
        stroke = {"focal": "{accent}", "external": "{link}"}.get(kind, "{line}")
        width = 2 if kind == "focal" else 1.2
        dash = ' stroke-dasharray="5 4"' if kind == "external" else ""
        radius = 20 if kind == "end" else 6
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{{node}}" stroke="{stroke}" stroke-width="{width}"{dash}/>']
        top = y + h / 2 - (len(lines) * 16) / 2 + 5
        out.append(f'<text x="{x + w / 2}" y="{top:g}" text-anchor="middle" font-size="14" font-weight="600" fill="{{ink}}">{escape(title)}</text>')
        for i, line in enumerate(lines):
            out.append(f'<text x="{x + w / 2}" y="{top + 17 + i * 16:g}" text-anchor="middle" font-size="12" fill="{{muted}}">{escape(line)}</text>')
        self.nodes.append("".join(out))

    def diamond(self, cx, cy, rx, ry, *lines):
        pts = f"{cx},{cy - ry} {cx + rx},{cy} {cx},{cy + ry} {cx - rx},{cy}"
        out = [f'<polygon points="{pts}" fill="{{node}}" stroke="{{accent}}" stroke-width="2"/>']
        top = cy - (len(lines) - 1) * 8 + 4
        for i, line in enumerate(lines):
            out.append(f'<text x="{cx}" y="{top + i * 16:g}" text-anchor="middle" font-size="12" font-weight="600" fill="{{ink}}">{escape(line)}</text>')
        self.nodes.append("".join(out))

    def arrow(self, *points, label=None, at=None, both=False, dashed=False):
        d = f"M {points[0][0]},{points[0][1]}"
        for i in range(1, len(points)):
            x, y = points[i]
            if i == len(points) - 1:
                d += f" L {x},{y}"
                break
            (px, py), (nx, ny) = points[i - 1], points[i + 1]
            sign = lambda v: (v > 0) - (v < 0)
            d += f" L {x - 8 * sign(x - px)},{y - 8 * sign(y - py)} Q {x},{y} {x + 8 * sign(nx - x)},{y + 8 * sign(ny - y)}"
        start = ' marker-start="url(#arrow)"' if both else ""
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.arrows.append(f'<path d="{d}" fill="none" stroke="{{muted}}" stroke-width="1.4"{dash}{start} marker-end="url(#arrow)"/>')
        if label:
            self.arrows.append(f'<text x="{at[0]}" y="{at[1]}" text-anchor="middle" font-size="12" fill="{{soft}}">{escape(label)}</text>')

    def note(self, x, y, text):
        self.nodes.append(f'<text x="{x}" y="{y}" font-size="12" fill="{{soft}}">{escape(text)}</text>')

    def write(self):
        for skin, colors in SKINS.items():
            body = "\n".join(self.zones + self.arrows + self.nodes)
            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'role="img" aria-labelledby="{self.name}-t {self.name}-d" font-family="{SANS}">\n'
                f'<title id="{self.name}-t">{escape(self.title)}</title>\n<desc id="{self.name}-d">{escape(self.desc)}</desc>\n'
                '<defs><marker id="arrow" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto-start-reverse" markerUnits="userSpaceOnUse">'
                '<polygon points="0 0, 9 4, 0 8" fill="{muted}"/></marker></defs>\n'
                '<rect width="100%" height="100%" rx="8" fill="{paper}"/>\n' + body + "\n</svg>\n")
            for role, value in colors.items():
                svg = svg.replace("{" + role + "}", value)
            (OUT / f"{self.name}-{skin}.svg").write_text(svg, encoding="utf-8", newline="\n")


# 1. Architecture ------------------------------------------------------------
d = Diagram("architecture", 960, 608, "Insurance CRM architecture",
            "A browser talks to Livewire pages in a Laravel app. The app runs queued searches and Artisan commands, "
            "calls boe.es, datoscif.es and the Claude API, and stores data in MySQL and PDFs on a private disk.")
d.zone(208, 24, 520, 440, "Laravel 12 app")
d.node(24, 320, 136, 72, "Agent", "Web browser")
d.node(232, 64, 200, 72, "Artisan commands", "2 daily + manual import")
d.node(232, 184, 200, 72, "Queued search job", "one day at a time")
d.node(232, 320, 200, 72, "Livewire pages", "login required", kind="focal")
d.node(504, 124, 200, 72, "BORME scraper", "download, parse, filter")
d.node(504, 228, 200, 64, "Company enrichment", "tax ID and website")
d.node(504, 360, 200, 72, "Policy comparison", "extract, filter, call")
d.node(784, 124, 152, 72, "boe.es", "BORME PDFs", kind="external")
d.node(784, 228, 152, 64, "datoscif.es", "company data", kind="external")
d.node(784, 360, 152, 72, "Claude API", "Messages", kind="external")
d.node(232, 512, 200, 72, "MySQL", "companies, acts, calls")
d.node(504, 512, 200, 72, "Private disk", "BORME and policy PDFs")
d.arrow((160, 356), (232, 356), both=True)
d.arrow((332, 320), (332, 256), label="dispatches", at=(374, 292))
d.arrow((432, 100), (468, 100), (468, 148), (504, 148))
d.arrow((432, 220), (468, 220), (468, 172), (504, 172))
d.arrow((432, 338), (476, 338), (476, 260), (504, 260))
d.arrow((432, 374), (468, 374), (468, 396), (504, 396))
d.arrow((704, 160), (784, 160))
d.arrow((704, 260), (784, 260))
d.arrow((704, 396), (784, 396))
d.arrow((332, 464), (332, 512), both=True)
d.arrow((604, 464), (604, 512), both=True)
d.write()

# 2. BORME to call -----------------------------------------------------------
d = Diagram("borme-to-call", 960, 568, "From a BORME notice to a scheduled call",
            "A search runs as a queued job over business days, downloads PDFs, extracts and filters notices, stores companies, "
            "and a daily command schedules a call when a company reaches ten months.")
X = [24, 264, 504, 744]
W, H = 192, 80
for x, (t, *ls) in zip(X, [("Search form", "province, dates,", "act types, sectors"), ("Queued job", "each business day,", "stops if cancelled"),
                           ("Daily BORME index", "finds the PDFs for", "Galician provinces"), ("Download PDFs", "in parallel, reusing", "files on disk")]):
    d.node(x, 24, W, H, t, *ls)
for x, (t, *ls) in zip(reversed(X), [("Extract text", "split into", "single notices"), ("Classify and parse", "keywords for the act,", "regex for the fields"),
                                     ("Filter", "act type, and CNAE", "or sector keyword"), ("Deduplicate and store", "tax ID, or name and", "municipality")]):
    d.node(x, 168, W, H, t, *ls)
for a in range(3):
    d.arrow((X[a] + W, 64), (X[a + 1], 64))
    d.arrow((X[a + 1], 208), (X[a] + W, 208))
d.arrow((840, 104), (840, 168))
d.node(24, 344, W, H, "Company record", "phone number", "added by hand")
d.arrow((120, 248), (120, 344))
d.diamond(384, 384, 128, 76, "Daily at 07:30:", "10 months old today,", "pending, phone,", "no calls yet?")
d.arrow((216, 384), (256, 384))
d.node(600, 344, 152, H, "Schedule call", "today at 09:00", kind="step")
d.arrow((512, 384), (600, 384), label="yes", at=(554, 374))
d.node(800, 344, 136, H, "Call agenda", "log the outcome", kind="end")
d.arrow((752, 384), (800, 384))
d.node(304, 496, 160, 48, "Not scheduled", kind="end")
d.arrow((384, 460), (384, 496), label="no", at=(404, 482))
d.note(504, 516, "A manual command can also import every company,")
d.note(504, 536, "without the filter step.")
d.write()

# 3. AI policy comparison ----------------------------------------------------
d = Diagram("ai-comparison", 960, 560, "AI policy comparison",
            "Text from two policy PDFs is extracted, filtered by keyword and capped at 25,000 characters each, then sent to the Claude API. "
            "Valid reports are saved; errors are logged and shown and nothing is saved.")
d.node(24, 24, W, H, "Two policy PDFs", "current policy", "and proposal")
d.node(264, 24, W, H, "Extract text", "PHP PDF parser")
d.node(504, 24, W, H, "Keyword filter", "coverage and price,", "plus 1 block each side")
d.node(744, 24, W, H, "Limit", "25,000 characters", "per PDF")
for a in range(3):
    d.arrow((X[a] + W, 64), (X[a + 1], 64))
d.node(744, 184, W, H, "Claude API", "fixed report prompt,", "120 s timeout", kind="external")
d.arrow((840, 104), (840, 184))
d.diamond(528, 224, 112, 64, "Complete", "response?")
d.arrow((744, 224), (640, 224))
d.node(192, 184, W, H, "Save report", "Markdown and date", "on the policy", kind="step")
d.arrow((416, 224), (384, 224), label="yes", at=(400, 214))
d.node(192, 344, W, H, "Policy tab", "agent can regenerate", "or delete the report", kind="end")
d.arrow((288, 264), (288, 344))
d.node(432, 344, W, H, "Error", "logged and shown,", "nothing saved")
d.arrow((528, 288), (528, 344), label="no", at=(548, 320))
d.note(24, 480, "Error cases: missing PDF or API key, no extractable text, failed HTTP call, empty answer, answer cut at the token limit.")
d.note(24, 502, "If no keyword matches, the first 25,000 characters are sent.")
d.arrow((360, 104), (360, 136), (672, 136), (672, 384), (624, 384), label="extraction error", at=(440, 128), dashed=True)
d.write()

# 4. VPS deployment ---------------------------------------------------
d = Diagram("vps-deployment", 960, 528, "VPS deployment",
            "The agent's browser reached nginx over HTTPS through the server firewall. nginx passed requests to PHP-FPM running the "
            "Laravel app, which used a MySQL server on the same machine. Supervisor kept a queue worker running, certbot renewed the "
            "certificate, cron ran the Laravel scheduler and updated dynamic DNS, and there were backups. The owner deployed over SSH.")
d.zone(208, 24, 728, 480, "Self-managed VPS, Ubuntu 24.04")
d.node(24, 96, 136, 72, "Agent", "Web browser")
d.node(24, 376, 136, 80, "Owner", "SSH key")
d.node(240, 72, 112, 400, "Firewall", "ufw")
d.node(432, 96, 136, 72, "nginx", "web server", kind="focal")
d.node(624, 96, 136, 72, "PHP-FPM 8.4", "Laravel app")
d.node(800, 96, 96, 72, "MySQL", "local only")
d.node(432, 248, 136, 72, "certbot timer", "TLS certificate")
d.node(624, 248, 136, 72, "Cron", "Laravel scheduler,", "dynamic DNS")
d.node(800, 248, 96, 72, "Backups")
d.node(416, 376, 152, 80, "Manual deploy", "git pull, composer,", "build, migrate")
d.node(624, 376, 136, 80, "Supervisor", "queue:work")
d.arrow((160, 132), (240, 132), label="HTTPS", at=(183, 122))
d.arrow((160, 416), (240, 416), label="SSH", at=(183, 406))
d.arrow((352, 132), (432, 132))
d.arrow((352, 416), (416, 416))
d.arrow((568, 132), (624, 132))
d.arrow((760, 132), (800, 132), both=True)
d.arrow((500, 248), (500, 168), label="renews", at=(526, 212))
d.arrow((692, 248), (692, 208), (848, 208), (848, 168), label="schedules calls", at=(770, 200))
d.arrow((568, 416), (624, 416), label="restart", at=(594, 406))
d.arrow((760, 416), (916, 416), (916, 132), (896, 132), label="BORME searches", at=(838, 406))
d.write()
