"""Documentation and deployment-package checks; no external calls."""
import io
import re
import struct
import unittest
import zipfile
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

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

    def test_legacy_ui_mockups_are_not_published(self):
        self.assertFalse(list((ROOT / "docs/images").glob("*.svg")))

    def test_telegram_uses_real_redacted_crops(self):
        guide = (ROOT / "README.md").read_text()
        provenance = (ROOT / "docs/TELAS.md").read_text()
        images = ROOT / "docs/images/telegram"
        expected = {
            "01-botfather-nome-username.png": (615, 266),
            "02-botfather-token-link.png": (422, 248),
            "03-telegram-vinculo.png": (605, 264),
            "04-telegram-teste-arquivo.png": (412, 92),
        }
        self.assertEqual({p.name for p in images.iterdir()}, set(expected))
        for name, dimensions in expected.items():
            with self.subTest(image=name):
                data = (images / name).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", data[16:24]), dimensions)
                self.assertIn(name, guide)
                self.assertIn(name, provenance)
        for phrase in ["nome de exibição", "username", "HTTP API", "tarja",
                       "não invalida o token original", "Conta vinculada!",
                       "Configuração concluída!", "não é o token do BotFather",
                       "Esse teste de áudio é adicional"]:
            self.assertIn(phrase, guide)
        self.assertNotIn("01-telegram-botfather.svg", guide)

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
                       "capturas reais", "Whisper", "Sempre por texto"]:
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
