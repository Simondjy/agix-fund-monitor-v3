import os
import tempfile
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt
import pandas as pd

class PDFReportGenerator:
    def __init__(self):
        self.story = []
        self.styles = getSampleStyleSheet()
        self.temp_dir = tempfile.mkdtemp()
        self.title_style = ParagraphStyle('CustomTitle', parent=self.styles['Heading1'], fontSize=16, spaceAfter=30, alignment=1)
        self.section_style = ParagraphStyle('CustomSection', parent=self.styles['Heading2'], fontSize=12, spaceAfter=12)
        self.normal_style = ParagraphStyle('CustomNormal', parent=self.styles['Normal'], fontSize=10, spaceAfter=6)

    def add_title(self, title):
        self.story.append(Paragraph(title, self.title_style))
        self.story.append(Spacer(1, 20))

    def add_section_title(self, title):
        self.story.append(Paragraph(title, self.section_style))
        self.story.append(Spacer(1, 10))

    def add_text(self, text):
        self.story.append(Paragraph(text, self.normal_style))
        self.story.append(Spacer(1, 6))

    def add_image(self, fig, caption=None):
        img_path = os.path.join(self.temp_dir, f"temp_img_{len(os.listdir(self.temp_dir))}.png")
        fig.savefig(img_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        img = Image(img_path, width=7*inch, height=5*inch)
        self.story.append(img)
        if caption:
            self.story.append(Paragraph(caption, self.normal_style))
        self.story.append(Spacer(1, 10))

    def add_dataframe(self, df, title=None):
        if title:
            self.add_section_title(title)
        data = [df.columns.tolist()]
        for _, row in df.iterrows():
            data.append([str(val) for val in row.values])
        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ])
        table.setStyle(style)
        self.story.append(table)
        self.story.append(Spacer(1, 10))

    def generate(self, filename):
        doc = SimpleDocTemplate(filename, pagesize=A4)
        doc.build(self.story)
        return filename

    def generate_download_link(self, filename):
        with open(filename, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download PDF Report</a>' 