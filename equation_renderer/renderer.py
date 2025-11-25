import tempfile
import subprocess
import base64
import os

def latex_to_png_base64(latex_code: str) -> str:
    """
    Convert ANY latex equation → PNG → base64
    Supports: xymatrix, amsmath, diagrams, etc.
    """

    contains_xymatrix = "\\xymatrix" in latex_code

    # wrap into display math unless it is a diagram
    if not contains_xymatrix:
        latex_code = "\\[\n" + latex_code + "\n\\]"

    with tempfile.TemporaryDirectory() as tmpdir:

        tex_file = os.path.join(tmpdir, "eq.tex")
        pdf_file = os.path.join(tmpdir, "eq.pdf")
        png_file = os.path.join(tmpdir, "eq.png")

        TEX_TEMPLATE = r"""
        \documentclass[varwidth=40cm]{standalone}
        \usepackage{amsmath, amssymb, amsfonts}
        \usepackage[all]{xy}
        \begin{document}
        %s
        \end{document}
        """ % latex_code

        # write .tex file
        with open(tex_file, "w") as f:
            f.write(TEX_TEMPLATE)

        # compile latex into pdf
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_file],
            cwd=tmpdir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if not os.path.exists(pdf_file):
            return None

        # pdf → png
        subprocess.run(
            ["convert", "-density", "300", pdf_file, "-quality", "100", png_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if not os.path.exists(png_file):
            return None

        # read image bytes → base64
        with open(png_file, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

