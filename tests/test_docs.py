"""Documentation and deployment-package checks; no external calls."""
import io
import re
import struct
import unittest
import zipfile
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "README.md", ROOT / "terraform/README.md", *sorted((ROOT / "docs").glob("*.md"))]


def anchors(text):
    headings = re.findall(r"^#{1,6} (.+)$", text, re.M)
    return {re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-") for heading in headings}


class DocumentationTests(unittest.TestCase):
    def test_local_links_resolve(self):
        for source in DOCS:
            for dest in re.findall(r"\]\(([^)]+)\)", source.read_text()):
                if dest.startswith(("https://", "http://")):
                    continue
                path, _, anchor = dest.partition("#")
                target = (source.parent / unquote(path)).resolve() if path else source
                with self.subTest(source=source.name, destination=dest):
                    self.assertTrue(target.is_file(), dest)
                    if anchor and target.suffix == ".md":
                        self.assertIn(unquote(anchor), anchors(target.read_text()))

    def test_only_telegram_remains_illustrated(self):
        images = sorted((ROOT / "docs/images").glob("*.svg"))
        self.assertEqual({p.name for p in images}, {
            "01-telegram-botfather.svg", "08-telegram-pareamento.svg",
            "09-telegram-conversa.svg",
        })
        guide = "\n".join(path.read_text() for path in DOCS)
        for path in images:
            with self.subTest(image=path.name):
                tree = ET.fromstring(path.read_text())
                self.assertEqual(tree.attrib["viewBox"], "0 0 1200 790")
                self.assertIn("Tela ilustrativa", "".join(tree.itertext()))
                self.assertIn(path.name, guide)
                self.assertNotIn("<script", path.read_text().lower())
                self.assertNotIn("https://api.telegram.org/bot", path.read_text())

    def test_console_captures_are_documented_pngs_outside_terraform(self):
        images = sorted((ROOT / "docs/images/console").glob("*.png"))
        self.assertGreaterEqual(len(images), 12)
        guide = (ROOT / "README.md").read_text()
        provenance = (ROOT / "docs/TELAS.md").read_text()
        for path in images:
            with self.subTest(image=path.name):
                content = path.read_bytes()
                self.assertEqual(content[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", content[16:24])
                self.assertGreaterEqual(width, 240)
                self.assertGreaterEqual(height, 120)
                self.assertLess(len(content), 1_000_000)
                self.assertIn(path.name, guide)
                self.assertIn(path.name, provenance)
        self.assertIn("21/09/2026", provenance)
        self.assertIn("não reconstruções", provenance)
        self.assertIn("não há capturas próprias dos resultados de Plan/Apply", provenance)
        self.assertFalse(list((ROOT / "terraform").rglob("*.png")))

    def test_deploy_button_is_only_after_prerequisites_and_preserves_context(self):
        guide = (ROOT / "README.md").read_text()
        deploy_urls = re.findall(
            r"https://cloud\.oracle\.com/resourcemanager/stacks/create\?[^)\s]+", guide)
        self.assertEqual(len(deploy_urls), 1)
        button_position = guide.index("[![Deploy to Oracle Cloud]")
        self.assertGreater(button_position, guide.index("## 2. Crie seu bot no Telegram"))
        self.assertGreater(button_position, guide.index("### Antes de abrir a Console"))
        self.assertLess(button_position, guide.index("## 4. Preencha as variáveis"))
        query = parse_qs(urlparse(deploy_urls[0]).query)
        self.assertEqual(query, {"zipUrl": [
            "https://github.com/rafaelrdias/oci-hermes-workshop/archive/refs/heads/resource-manager.zip"
        ]})
        for phrase in ["GitHub = instruções", "Console OCI = execução", "nova aba",
                       "Ponto de retorno", "Desmarque Run apply", "Welcome!",
                       "Package URL", "Automatically approve"]:
            self.assertIn(phrase, guide)

    def test_output_titles_match_actual_schema_labels(self):
        schema = (ROOT / "terraform/schema.yaml").read_text()
        guide = (ROOT / "README.md").read_text().replace("\n   ", " ")
        ssh = (ROOT / "docs/SSH.md").read_text().replace("\n   ", " ")
        for title in ["Desbloqueie, copie e envie este comando em DM ao seu bot",
                      "Como concluir", "Modelo OCI on-demand"]:
            self.assertIn(title, schema)
            self.assertIn(title, guide)
        for title in ["SSH opcional — guarde sua chave privada em segurança",
                      "Chave PRIVADA gerada: revelar, copiar e salvar como hermes.key (vazio se não gerada)"]:
            self.assertIn(title, schema)
            self.assertIn(title, ssh)

    def test_deployment_branch_and_version_are_consistent(self):
        schema = (ROOT / "terraform/schema.yaml").read_text()
        version = re.search(r"^version: '([^']+)'", schema, re.M).group(1)
        for source in [ROOT / "README.md", ROOT / "terraform/README.md"]:
            self.assertIn(version, source.read_text())
            self.assertIn("heads/resource-manager.zip", source.read_text())
        self.assertIn("default: hermes-evento", schema)
        self.assertIn('default = "hermes-evento"', (ROOT / "terraform/variables.tf").read_text())

    def test_guide_has_all_separate_consents_and_pairing(self):
        guide = (ROOT / "README.md").read_text()
        for phrase in ["Application information", "telegram_pairing_command",
                       "a Stack que acabou de executar", "três aceites distintos",
                       "telas ilustrativas", "Whisper", "Sempre por texto"]:
            self.assertIn(phrase, guide)

    def test_terraform_package_is_small_and_has_no_artifacts(self):
        files = [p for p in (ROOT / "terraform").rglob("*") if p.is_file()
                 and not any(part in {".terraform", "__pycache__"} for part in p.parts)]
        forbidden = {".pem", ".key", ".tfstate", ".tfplan", ".pptx", ".pdf", ".zip"}
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                self.assertNotIn(path.suffix, forbidden, path.name)
                self.assertNotEqual(path.name, "terraform.tfvars")
                archive.writestr(str(path.relative_to(ROOT / "terraform")), path.read_bytes())
        self.assertLess(len(memory.getvalue()), 1_000_000)


if __name__ == "__main__":
    unittest.main()
