"""Build Bitcoin_Volatility_Case.ipynb from analysis.py ('# %%' cells) and interpretations.py (INTERP dict)."""
import re, sys, pathlib
import nbformat as nbf

here = pathlib.Path(__file__).parent
src = (here / "analysis.py").read_text()
try:
    sys.path.insert(0, str(here)); from interpretations import INTERP
except ImportError:
    INTERP = {}

cells = []
for block in re.split(r"^# %%", src, flags=re.M)[1:]:
    is_md = block.startswith(" [markdown]")
    body = block.split("\n", 1)[1].strip("\n")
    if is_md:
        text = "\n".join(l[2:] if l.startswith("# ") else l.lstrip("#") for l in body.split("\n"))
        for k, v in INTERP.items():
            text = text.replace(k, v)
        cells.append(nbf.v4.new_markdown_cell(text))
    else:
        cells.append(nbf.v4.new_code_cell(body))
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, here / "Bitcoin_Volatility_Case.ipynb")
print("cells:", len(cells))
