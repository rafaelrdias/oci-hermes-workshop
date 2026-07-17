#!/usr/bin/env python3
"""Generate the facilitator checklist PDF for the OCI Hermes workshop."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "checklist-facilitador-hermes-oci.pdf"

ORACLE_RED = colors.HexColor("#C74634")
INK = colors.HexColor("#172B3A")
MUTED = colors.HexColor("#536575")
LIGHT = colors.HexColor("#F3F5F7")
LINE = colors.HexColor("#D7DEE3")
SUCCESS = colors.HexColor("#167D65")


class CheckboxItem(Flowable):
    """A checkbox followed by a wrapping paragraph."""

    def __init__(self, text, style, box_color=ORACLE_RED):
        super().__init__()
        self.paragraph = Paragraph(text, style)
        self.box_color = box_color
        self.box_size = 9
        self.gap = 8

    def wrap(self, available_width, available_height):
        text_width = available_width - self.box_size - self.gap
        _, text_height = self.paragraph.wrap(text_width, available_height)
        self.width = available_width
        self.height = max(self.box_size, text_height) + 5
        self.text_width = text_width
        self.text_height = text_height
        return self.width, self.height

    def draw(self):
        y = self.height - self.box_size - 1
        self.canv.setStrokeColor(self.box_color)
        self.canv.setLineWidth(1)
        self.canv.roundRect(0, y, self.box_size, self.box_size, 1.5, stroke=1, fill=0)
        self.paragraph.drawOn(self.canv, self.box_size + self.gap, self.height - self.text_height)


def draw_page(canvas, document):
    width, height = A4
    canvas.saveState()

    canvas.setFillColor(ORACLE_RED)
    canvas.rect(0, height - 12 * mm, width, 12 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(17 * mm, height - 7.7 * mm, "ORACLE CLOUD + HERMES AGENT")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 17 * mm, height - 7.7 * mm, "TDC Florianópolis")

    canvas.setStrokeColor(LINE)
    canvas.line(17 * mm, 14 * mm, width - 17 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(17 * mm, 9.5 * mm, "Checklist do facilitador - Workshop de 90 minutos")
    canvas.drawRightString(width - 17 * mm, 9.5 * mm, f"Pagina {document.page}")
    canvas.restoreState()


def build_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=5 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=MUTED,
            spaceAfter=5 * mm,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13.5,
            leading=16,
            textColor=INK,
            spaceBefore=4 * mm,
            spaceAfter=2.5 * mm,
            keepWithNext=True,
        ),
        "item": ParagraphStyle(
            "Item",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.8,
            textColor=INK,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            leftIndent=12,
            firstLineIndent=-8,
            bulletIndent=0,
            textColor=INK,
            spaceAfter=2.5,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.3,
            leading=11,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=6.8,
            leading=9.2,
            textColor=INK,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.3,
            leading=13,
            textColor=SUCCESS,
            alignment=TA_CENTER,
        ),
    }


def section(title, items, styles):
    return KeepTogether(
        [Paragraph(title, styles["section"])]
        + [CheckboxItem(item, styles["item"]) for item in items]
    )


def bullet_section(title, items, styles, color=ORACLE_RED):
    flows = [Paragraph(title, styles["section"])]
    bullet_style = ParagraphStyle(
        f"Bullet-{color.hexval()}",
        parent=styles["bullet"],
        bulletColor=color,
    )
    for item in items:
        flows.append(Paragraph(item, bullet_style, bulletText="●"))
    return KeepTogether(flows)


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()

    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=17 * mm,
        rightMargin=17 * mm,
        topMargin=20 * mm,
        bottomMargin=19 * mm,
        title="Checklist do facilitador - Hermes Agent na OCI",
        author="Oracle / TDC Florianópolis",
        subject="Preparação e condução do workshop Hermes Agent com OCI e Telegram",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="main",
    )
    document.addPageTemplates([PageTemplate(id="checklist", frames=[frame], onPage=draw_page)])

    story = [
        Spacer(1, 4 * mm),
        Paragraph("Checklist do facilitador", styles["title"]),
        Paragraph(
            "Hermes Agent na OCI pelo Telegram - roteiro operacional para preparar, conduzir e encerrar o laboratório com segurança.",
            styles["subtitle"],
        ),
        Table(
            [[
                Paragraph("90 MIN<br/><font size='7'>duração total</font>", styles["meta"]),
                Paragraph("60 MIN<br/><font size='7'>atividade guiada</font>", styles["meta"]),
                Paragraph("30 MIN<br/><font size='7'>dúvidas e recuperação</font>", styles["meta"]),
            ]],
            colWidths=[document.width / 3] * 3,
            rowHeights=[18 * mm],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]),
        ),
        Spacer(1, 3 * mm),
        section(
            "Uma semana antes",
            [
                "Confirmar o tipo e os limites das contas Trial dos participantes.",
                "Confirmar que todos podem criar policy na tenancy ou preparar a policy centralmente.",
                "Confirmar subscription da região <b>us-chicago-1</b>.",
                "Testar disponibilidade on-demand de <b>openai.gpt-oss-120b</b>.",
                "Gerar novamente o ZIP do Resource Manager.",
                "Executar um ensaio do zero com uma conta limpa.",
                "Validar a tag do Hermes fixada em <b>hermes_git_ref</b>.",
            ],
            styles,
        ),
        section(
            "Um dia antes",
            [
                "Testar a VM de demonstração e executar <b>hermes doctor</b>.",
                "Inserir uma OCI Generative AI API key válida na VM de demonstração.",
                "Criar um bot exclusivo para a demonstração e configurar allowlist.",
                "Validar um turno completo no Telegram.",
                "Separar uma VM pronta como plano B.",
                "Disponibilizar o repositorio, o ZIP e um QR code para o link.",
            ],
            styles,
        ),
        PageBreak(),
        Paragraph("Antes da sala abrir", styles["section"]),
        Table(
            [[Preformatted(
                "ssh -i /caminho/chave opc@147.224.210.244 'hermes --version'\n"
                "ssh -i /caminho/chave opc@147.224.210.244 'sudo systemctl status hermes-gateway --no-pager'\n"
                "ssh -i /caminho/chave opc@147.224.210.244 'sudo journalctl -u hermes-gateway -n 50 --no-pager'",
                styles["code"],
            )]],
            colWidths=[document.width],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]),
        ),
        Spacer(1, 2.5 * mm),
        CheckboxItem("Deixar a OCI Console já na região Chicago.", styles["item"]),
        CheckboxItem("Abrir <b>@BotFather</b> e <b>@userinfobot</b> no celular de demonstração.", styles["item"]),
        CheckboxItem("Ter tenancy OCID, compartment OCID e chave pública em um bloco local.", styles["item"]),
        CheckboxItem("Cronometrar a atividade em 60 minutos.", styles["item"]),
        bullet_section(
            "Estratégia de facilitação",
            [
                "O Terraform começa primeiro; API key e bot são criados enquanto cloud-init roda.",
                "Participante que travar por mais de 3 minutos recebe o checkpoint ou a VM pronta.",
                "Erros comuns são tratados coletivamente; erros específicos recebem ajuda individual durante o próximo bloco.",
                "Aos 55 minutos, interromper novas configurações e demonstrar o resultado na VM de backup.",
            ],
            styles,
            SUCCESS,
        ),
        bullet_section(
            "Não fazer",
            [
                "Não pedir que participantes colem tokens no chat da sala.",
                "Não usar <b>GATEWAY_ALLOW_ALL_USERS=true</b>.",
                "Não abrir a porta 8642 ou portas de webhook.",
                "Não demonstrar comandos destrutivos pelo Telegram.",
                "Não deixar recursos Trial rodando sem combinar a destruição.",
            ],
            styles,
            ORACLE_RED,
        ),
        Spacer(1, 4 * mm),
        Table(
            [[Paragraph(
                "Critério de prontidão: Terraform validado, VM acessível, gateway ativo, OCI respondendo e um turno completo no Telegram.",
                styles["callout"],
            )]],
            colWidths=[document.width],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF5F1")),
                ("BOX", (0, 0), (-1, -1), 0.8, SUCCESS),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]),
        ),
    ]

    document.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()
