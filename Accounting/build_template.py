"""Builds the IESE Financial Accounting homework template (T-accounts -> B/S -> I/S -> C/F)."""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter as L

OUT = sys.argv[1]
FONT = "Arial"
NUM = '#,##0;-#,##0;"-"'
PCT = '0.0%;-0.0%;"-"'

# ---- palette (user's original colours kept for the balance sheet) ----
A_DARK, A_LIGHT = "D62E4E", "FFD7D7"      # assets (red family)
L_DARK, L_LIGHT = "729FCF", "B4C7DC"      # liabilities & OE (blue family)
OE_LIGHT = "DDE8F3"                      # owners' equity accounts (lighter blue)
PL_LIGHT = "FFF2CC"                      # P&L account (yellow)
IS_DARK, IS_LIGHT, IS_SUB = "2E7D32", "C8E6C9", "E8F5E9"   # income statement (green)
CF_DARK = "6A1B9A"                                         # cash flow (purple)
CFO_L, CFI_L, CFF_L = "E1BEE7", "FFE0B2", "B2EBF2"
GREY, NOTE = "F2F2F2", "FFFBEA"
INPUT_BLUE = "0000FF"

def fill(c): return PatternFill("solid", start_color=c, end_color=c)
thin = Side(style="thin", color="000000")
med = Side(style="medium", color="000000")
hair = Side(style="thin", color="BFBFBF")

def font(bold=False, color="000000", size=10, italic=False):
    return Font(name=FONT, bold=bold, color=color, size=size, italic=italic)

def put(ws, ref, value=None, bold=False, color="000000", bg=None, size=10, italic=False,
        num=None, align=None, wrap=False, border=None):
    c = ws[ref]
    if value is not None:
        c.value = value
        if isinstance(value, str) and value.startswith("= "):
            c.data_type = "s"   # a label such as '= Gross profit', not a formula
    c.font = font(bold, color, size, italic)
    if bg: c.fill = fill(bg)
    if num: c.number_format = num
    if align or wrap: c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    if border: c.border = border
    return c

def merge(ws, rng, value, bold=True, color="000000", bg=None, size=10, align="center", wrap=False, italic=False):
    ws.merge_cells(rng)
    first = rng.split(":")[0]
    put(ws, first, value, bold, color, bg, size, italic, align=align, wrap=wrap)
    if bg:
        for row in ws[rng]:
            for c in row: c.fill = fill(bg)
    return ws[first]

def check_formula(expr):
    return f'=IF(ABS({expr})<0.5,"OK","ERROR: "&TEXT({expr},"#,##0"))'

def add_ok_format(ws, rng):
    first = rng.split(":")[0].replace("$", "")
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{first}="OK"'], fill=fill("C6EFCE"), font=Font(name=FONT, bold=True, color="006100")))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'LEFT({first},5)="ERROR"'], fill=fill("FFC7CE"), font=Font(name=FONT, bold=True, color="9C0006")))

def notes(ws, col, start_row, lines, width=78, title="Notes & reminders"):
    ws.column_dimensions[col].width = width
    put(ws, f"{col}{start_row}", title, bold=True, color="FFFFFF", bg="595959")
    r = start_row + 1
    for ln in lines:
        bold = ln.startswith("#")
        put(ws, f"{col}{r}", ln.lstrip("# "), bold=bold, bg=NOTE, wrap=True, size=9)
        r += 1
    return r

wb = Workbook()

# =====================================================================
# 1. GUIDE
# =====================================================================
g = wb.active
g.title = "Guide"
g.sheet_view.showGridLines = False
for col, w in zip("ABCDEFG", [2, 34, 20, 20, 20, 30, 2]):
    g.column_dimensions[col].width = w
merge(g, "B1:F1", "FINANCIAL ACCOUNTING HOMEWORK TEMPLATE", bg="404040", color="FFFFFF", size=14)
put(g, "B3", "Company name", bold=True)
put(g, "C3", "Company X", color=INPUT_BLUE, bg="FFFF00")
put(g, "B4", "Period (e.g. Year 1)", bold=True)
put(g, "C4", "Year 1", color=INPUT_BLUE, bg="FFFF00")
put(g, "B5", "Currency / units", bold=True)
put(g, "C5", "€", color=INPUT_BLUE, bg="FFFF00")
put(g, "D3", "← fill in once, every sheet picks it up", italic=True, size=9)

r = 7
merge(g, f"B{r}:F{r}", "WORKFLOW (do the sheets in this order)", bg="595959", color="FFFFFF", align="left"); r += 1
for step in [
    "1. Journal: write every transaction as a journal entry (Dr = Cr). Give each entry a number (1, 2, 3a, 3b, …, CE).",
    "2. T-Accounts: post each entry to its T-accounts, writing the entry # in the grey # columns. Beginning balances go on the BB row.",
    "3. Balance Sheet: fills itself from the T-accounts (beginning and ending balances). Check that Assets = L + OE.",
    "4. Income Statement: type the revenues/expenses from the P&L T-account. Expenses and losses go in as NEGATIVE numbers.",
    "5. Cash Flow: type each cash movement from the Cash T-account in the direct method. The indirect method fills itself.",
    "6. CF Worksheet (optional): the course's ΔCash = −ΔA* + ΔL + ΔOE table. Use it to check the indirect method line by line.",
    "7. Every check cell must say OK in green. A red ERROR tells you how far off you are.",
]:
    merge(g, f"B{r}:F{r}", step, bold=False, align="left", wrap=True); g.row_dimensions[r].height = 26; r += 1

r += 1
merge(g, f"B{r}:F{r}", "COLOUR LEGEND", bg="595959", color="FFFFFF", align="left"); r += 1
legend = [
    ("1,000", INPUT_BLUE, None, "Blue text = number you type in (input)"),
    ("1,000", "000000", None, "Black text = formula (don't type over it)"),
    ("Assets", "FFFFFF", A_DARK, "Asset section header (your red)"),
    ("Account", "000000", A_LIGHT, "Asset T-account title"),
    ("L & OE", "FFFFFF", L_DARK, "Liabilities & owners' equity section header (your blue)"),
    ("Account", "000000", L_LIGHT, "Liability T-account title"),
    ("Account", "000000", OE_LIGHT, "Owners' equity T-account title"),
    ("P&L", "000000", PL_LIGHT, "Profit & loss for the period (temporary OE account)"),
    ("I/S", "FFFFFF", IS_DARK, "Income statement (green family)"),
    ("C/F", "FFFFFF", CF_DARK, "Cash flow statement (purple, with orange for CFI and cyan for CFF)"),
    ("OK", "006100", "C6EFCE", "Check passed"),
    ("ERROR", "9C0006", "FFC7CE", "Check failed. The number is the difference."),
]
for sample, fc, bg, txt in legend:
    put(g, f"B{r}", sample, bold=True, color=fc, bg=bg, align="center")
    merge(g, f"C{r}:F{r}", txt, bold=False, align="left"); r += 1

r += 1
merge(g, f"B{r}:F{r}", "DEBIT / CREDIT RULES (CN-230-E, T-accounts section)", bg="595959", color="FFFFFF", align="left"); r += 1
for i, h in enumerate(["Account type", "Increase", "Decrease", "Normal balance", "Examples"]):
    put(g, f"{'BCDEF'[i]}{r}", h, bold=True, bg=GREY, border=Border(bottom=thin))
r += 1
rules = [
    ("Assets", "Debit (left)", "Credit (right)", "Debit", "Cash, A/R, inventory, PPE"),
    ("Contra-assets", "Credit", "Debit", "Credit", "Accumulated depreciation / amortization"),
    ("Liabilities", "Credit", "Debit", "Credit", "A/P, taxes payable, loans"),
    ("Owners' equity", "Credit", "Debit", "Credit", "Share capital, retained profits"),
    ("P&L: revenues & gains", "Credit", "", "Credit", "Sales, financial income"),
    ("P&L: expenses & losses", "Debit", "", "Debit", "COGS, salaries, depreciation, tax"),
]
for row in rules:
    for i, v in enumerate(row):
        put(g, f"{'BCDEF'[i]}{r}", v, bold=(i == 0))
    r += 1
merge(g, f"B{r}:F{r}", "Every entry: total debits = total credits.  A = L + OE always holds.  Debit/credit mean LEFT/RIGHT, not +/−.", bold=False, align="left", italic=True); r += 1
merge(g, f"B{r}:F{r}", "Closing entry (CE): Dr Profit for the period / Cr Retained profits (net profit). After it the P&L account is zero.", bold=False, align="left", italic=True); r += 1
merge(g, f"B{r}:F{r}", "Dividends are NOT an expense: Dr Retained profits / Cr Cash (or Dividends payable).", bold=False, align="left", italic=True); r += 1

r += 1
merge(g, f"B{r}:F{r}", "EXAMPLE JOURNAL ENTRY (from the course note: a €10,000 loan received in cash)", bg="595959", color="FFFFFF", align="left"); r += 1
for i, h in enumerate(["#  /  Account", "Dr", "Cr", "Effect", "Cash flow class"]):
    put(g, f"{'BCDEF'[i]}{r}", h, bold=True, bg=GREY, border=Border(bottom=thin))
r += 1
for row in [("1  Cash", 10000, None, "A+", "F (new loan)"), ("1  Long-term bank loan", None, 10000, "L+", "")]:
    for i, v in enumerate(row):
        put(g, f"{'BCDEF'[i]}{r}", v, num=NUM if i in (1, 2) else None, color=INPUT_BLUE if i in (1, 2) else "000000")
    r += 1

r += 1
merge(g, f"B{r}:F{r}", "CASH FLOW CLASSIFICATION (CN-233-E)", bg="595959", color="FFFFFF", align="left"); r += 1
for lab, txt, bg in [
    ("Operating (CFO)", "Collections from customers, payments to suppliers / employees / rent / utilities, INTEREST paid & received, TAXES paid, dividends received.", CFO_L),
    ("Investing (CFI)", "Purchase / sale of land, buildings, PPE, intangibles (software), shares of other firms, marketable securities that are not cash equivalents.", CFI_L),
    ("Financing (CFF)", "Share issues, NEW loans received, loan / mortgage PRINCIPAL repaid, dividends paid.", CFF_L),
    ("Not cash at all", "Depreciation, amortization, purchases on credit, gains/losses on disposals. They go in the indirect method as adjustments only.", GREY),
    ("Cash equivalents", "Investments maturing in under 3 months count as CASH. Those maturing in 3 to 12 months are marketable securities (investing).", GREY),
]:
    put(g, f"B{r}", lab, bold=True, bg=bg)
    merge(g, f"C{r}:F{r}", txt, bold=False, align="left", wrap=True); g.row_dimensions[r].height = 26; r += 1

r += 1
merge(g, f"B{r}:F{r}", "KEY FORMULAS", bg="595959", color="FFFFFF", align="left"); r += 1
for lab, txt in [
    ("Accounting identity", "A = L + OE     (net assets: A − L = OE)"),
    ("Change in cash", "ΔCash = −ΔAssets other than cash + ΔL + ΔOE   (Δ = ending − beginning)"),
    ("Working capital", "Current assets − current liabilities"),
    ("CFO (indirect)", "Net profit + depreciation & amortization + non-operating losses − non-operating gains − ΔOperating assets + ΔOperating liabilities"),
    ("Free cash flow", "CFO − capex (in the course example: CFO + CFI = 93 − 69 = 24)"),
    ("Gain / loss on sale", "Selling price − book value (cost − accumulated depreciation) of the asset sold"),
]:
    put(g, f"B{r}", lab, bold=True)
    merge(g, f"C{r}:F{r}", txt, bold=False, align="left", wrap=True); g.row_dimensions[r].height = 26; r += 1

r += 1
merge(g, f"B{r}:F{r}", "HOW TO MERGE CELLS / ADD ROWS", bg="595959", color="FFFFFF", align="left"); r += 1
for lab, txt in [
    ("Excel", "Select the cells → Home tab → 'Merge & Center' (the drop-down arrow also offers 'Merge Across' and 'Unmerge Cells')."),
    ("LibreOffice Calc", "Select the cells → Format menu → Merge and Unmerge Cells → Merge and Center Cells (or the Merge button on the toolbar). If it asks, choose to keep only the first cell's content."),
    ("Tip", "Merge only titles and headers, never cells that hold numbers. Formulas and sorting break on merged number cells."),
    ("Need more lines in a T?", "Right-click a row number INSIDE the T (between BB and Total) → Insert Rows. The Total/EB SUMs stretch automatically. Inserting a row affects the whole sheet row, so both T-accounts on that row get it."),
]:
    put(g, f"B{r}", lab, bold=True)
    merge(g, f"C{r}:F{r}", txt, bold=False, align="left", wrap=True); g.row_dimensions[r].height = 30; r += 1

COMPANY = "Guide!$C$3"
PERIOD = "Guide!$C$4"
CUR = "Guide!$C$5"

# =====================================================================
# 2. T-ACCOUNTS
# =====================================================================
t = wb.create_sheet("T-Accounts")
t.sheet_view.showGridLines = False
ENTRY_ROWS = 15
T_HEIGHT = 1 + 1 + 1 + ENTRY_ROWS + 1 + 1 + 1   # title, header, BB, entries, total, EB, spacer
TOP = 7
# column blocks: (ref, dr, cr, ref)
BLOCKS = {"A1": 2, "A2": 7, "L1": 13, "L2": 18}   # start column index
widths = {1: 2, 6: 2, 11: 4, 12: 2, 17: 2, 22: 3}
for blk, c0 in BLOCKS.items():
    widths[c0] = 4.5; widths[c0 + 1] = 12; widths[c0 + 2] = 12; widths[c0 + 3] = 4.5
for c, w in widths.items():
    t.column_dimensions[L(c)].width = w

# kind: A (asset), CA (contra-asset), L (liability), OE, PL
ASSETS = [
    [("cash", "Cash & cash equivalents", "A"), ("mktsec", "Marketable securities", "A")],
    [("ar", "Accounts receivable", "A"), ("inv", "Inventories", "A")],
    [("prepaid", "Prepaid rent / prepaid expenses", "A"), ("other_ca", "Other current asset (rename)", "A")],
    [("land", "Land", "A"), ("fininv", "Financial investments (LT shares)", "A")],
    [("bldg", "Buildings", "A"), ("ad_bldg", "Accum. depreciation – Buildings", "CA")],
    [("fe", "Furniture & equipment", "A"), ("ad_fe", "Accum. depreciation – Furn. & equip.", "CA")],
    [("sw", "Software / intangible assets", "A"), ("am_sw", "Accumulated amortization", "CA")],
]
LOE = [
    [("ap", "Accounts payable", "L"), ("salp", "Salaries payable", "L")],
    [("intp", "Interest payable", "L"), ("taxp", "Taxes payable", "L")],
    [("dep", "Deposits from customers (unearned rev.)", "L"), ("divp", "Dividends payable", "L")],
    [("stloan", "Short-term loans / current portion LTD", "L"), ("other_l", "Other liability (rename)", "L")],
    [("ltloan", "Long-term bank loan", "L"), ("mort", "Mortgage / obligations on land & bldgs", "L")],
    [("sc", "Share capital", "OE"), ("sp", "Share premium", "OE")],
    [("rp", "Retained profits", "OE"), ("pl", "Profit & loss for the period (P&L)", "PL")],
]
ACC = {}   # key -> dict of cell refs

def build_T(key, name, kind, r0, c0):
    ref_l, dr, cr, ref_r = L(c0), L(c0 + 1), L(c0 + 2), L(c0 + 3)
    title_bg = {"A": A_LIGHT, "CA": A_LIGHT, "L": L_LIGHT, "OE": OE_LIGHT, "PL": PL_LIGHT}[kind]
    tag = {"A": "(A)", "CA": "(contra-A)", "L": "(L)", "OE": "(OE)", "PL": "(OE – temporary)"}[kind]
    merge(t, f"{ref_l}{r0}:{ref_r}{r0}", name, bg=title_bg, size=10)
    put(t, f"{ref_r}{r0}")
    debit_normal = kind == "A"
    hdr = [("#", None), ("Dr (+)" if debit_normal else "Dr (−)", None), ("Cr (−)" if debit_normal else "Cr (+)", None), ("#", None)]
    if kind == "PL":
        hdr = [("#", None), ("Dr: expenses", None), ("Cr: revenues", None), ("#", None)]
    for i, (h, _) in enumerate(hdr):
        put(t, f"{L(c0 + i)}{r0 + 1}", h, bold=True, align="center", size=8,
            border=Border(bottom=med, right=med if i == 1 else None))
    t[f"{ref_r}{r0 + 1}"].value = tag if False else "#"
    bb = r0 + 2
    first, last = bb, r0 + 2 + ENTRY_ROWS
    tot, eb = last + 1, last + 2
    for rr in range(bb, last + 1):
        for i in range(4):
            col = L(c0 + i)
            is_ref = i in (0, 3)
            c = put(t, f"{col}{rr}", color="7F7F7F" if is_ref else INPUT_BLUE, bg=GREY if is_ref else None,
                    num=None if is_ref else NUM, align="center" if is_ref else None, size=8 if is_ref else 10,
                    border=Border(right=med if i == 1 else None, bottom=hair))
    # BB label on the natural side
    if debit_normal:
        t[f"{ref_l}{bb}"].value = "BB"
    else:
        t[f"{ref_r}{bb}"].value = "BB"
    for i in range(4):
        t[f"{L(c0 + i)}{bb}"].fill = fill("EDEDED")
    t[f"{ref_l}{bb}"].font = font(True, "000000", 8)
    t[f"{ref_r}{bb}"].font = font(True, "000000", 8)
    # totals
    put(t, f"{ref_l}{tot}", "Tot", bold=True, size=8, align="center", border=Border(top=thin))
    put(t, f"{dr}{tot}", f"=SUM({dr}{first}:{dr}{last})", bold=True, num=NUM, border=Border(top=thin, right=med))
    put(t, f"{cr}{tot}", f"=SUM({cr}{first}:{cr}{last})", bold=True, num=NUM, border=Border(top=thin))
    put(t, f"{ref_r}{tot}", "Tot", bold=True, size=8, align="center", border=Border(top=thin))
    # ending balance on the natural side
    if debit_normal:
        put(t, f"{ref_l}{eb}", "EB", bold=True, size=8, align="center", bg=title_bg)
        put(t, f"{dr}{eb}", f"={dr}{tot}-{cr}{tot}", bold=True, num=NUM, bg=title_bg, border=Border(top=thin, bottom=med, right=med))
        eb_ref = f"{dr}{eb}"; bb_ref = f"{dr}{bb}"
    else:
        put(t, f"{ref_r}{eb}", "EB", bold=True, size=8, align="center", bg=title_bg)
        put(t, f"{cr}{eb}", f"={cr}{tot}-{dr}{tot}", bold=True, num=NUM, bg=title_bg, border=Border(top=thin, bottom=med))
        eb_ref = f"{cr}{eb}"; bb_ref = f"{cr}{bb}"
    t[f"{dr}{eb}" if not debit_normal else f"{cr}{eb}"].border = Border(top=thin, right=None)
    if not debit_normal:
        t[f"{dr}{eb}"].border = Border(top=thin, right=med)
    ACC[key] = dict(name=name, kind=kind, title=f"'T-Accounts'!${ref_l}${r0}", bb=f"'T-Accounts'!${bb_ref.rstrip('0123456789')}${bb}",
                    eb=f"'T-Accounts'!${eb_ref.rstrip('0123456789')}${eb}",
                    dr_rng=f"'T-Accounts'!${dr}${first}:${dr}${last}", cr_rng=f"'T-Accounts'!${cr}${first}:${cr}${last}",
                    refl_rng=f"'T-Accounts'!${ref_l}${first}:${ref_l}${last}", refr_rng=f"'T-Accounts'!${ref_r}${first}:${ref_r}${last}",
                    dr_tot=f"{dr}{tot}", cr_tot=f"{cr}{tot}", dr_bb=f"{dr}{bb}", cr_bb=f"{cr}{bb}")

merge(t, "B1:T1", "T-ACCOUNTS (general ledger)", bg="404040", color="FFFFFF", size=14)
put(t, "B2", "Company:", bold=True); t.merge_cells("D2:I2"); put(t, "D2", f"={COMPANY}")
put(t, "L2", "Period:", bold=True); t.merge_cells("N2:R2"); put(t, "N2", f"={PERIOD}")
merge(t, f"B{TOP - 2}:J{TOP - 2}", "ASSETS  (uses of capital)", bg=A_DARK, color="FFFFFF", size=12)
merge(t, f"L{TOP - 2}:T{TOP - 2}", "OWNERS' EQUITY & LIABILITIES  (sources of capital)", bg=L_DARK, color="FFFFFF", size=12)

for i, pair in enumerate(ASSETS):
    r0 = TOP + i * T_HEIGHT
    build_T(*pair[0], r0, BLOCKS["A1"]); build_T(*pair[1], r0, BLOCKS["A2"])
for i, pair in enumerate(LOE):
    r0 = TOP + i * T_HEIGHT
    build_T(*pair[0], r0, BLOCKS["L1"]); build_T(*pair[1], r0, BLOCKS["L2"])

# section labels on the left margin (merged vertical strip in column K spacer)
end_row = TOP + len(ASSETS) * T_HEIGHT
# trial-balance check (debits posted = credits posted, excluding beginning balances)
cr_ = end_row + 1
dr_parts = "+".join(f"{a['dr_tot']}" for a in ACC.values())
cr_parts = "+".join(f"{a['cr_tot']}" for a in ACC.values())
bb_dr = "+".join(f"{a['dr_bb']}" for a in ACC.values())
bb_cr = "+".join(f"{a['cr_bb']}" for a in ACC.values())
merge(t, f"B{cr_}:J{cr_}", "Total debits posted (excl. BB)", bold=True, align="right", bg=GREY)
put(t, f"L{cr_}", f"=({dr_parts})-({bb_dr})", bold=True, num=NUM)
t.merge_cells(f"L{cr_}:N{cr_}")
merge(t, f"B{cr_ + 1}:J{cr_ + 1}", "Total credits posted (excl. BB)", bold=True, align="right", bg=GREY)
put(t, f"L{cr_ + 1}", f"=({cr_parts})-({bb_cr})", bold=True, num=NUM)
t.merge_cells(f"L{cr_ + 1}:N{cr_ + 1}")
merge(t, f"B{cr_ + 2}:J{cr_ + 2}", "CHECK: debits = credits", bold=True, align="right", bg=GREY)
put(t, f"L{cr_ + 2}", check_formula(f"L{cr_}-L{cr_ + 1}"), bold=True, align="center")
t.merge_cells(f"L{cr_ + 2}:N{cr_ + 2}")
add_ok_format(t, f"L{cr_ + 2}")
T_CHECK = f"'T-Accounts'!$L${cr_ + 2}"

notes(t, "W", TOP - 2, [
    "# How to post",
    "Write the amount on the correct side and the journal entry # in the grey column next to it, e.g. 1, 2, 3a, CE.",
    "BB = beginning balance (from last period's balance sheet). Leave empty for a new company.",
    "EB = ending balance. It is calculated for you and always sits on the account's normal side.",
    "# Asset side (Uses of capital)",
    "Debit (+) increases, Credit (−) decreases. Normal balance is on the debit side.",
    "# Liabilities & OE side (Sources of capital)",
    "Debit (−) decreases, Credit (+) increases. Normal balance is on the credit side.",
    "# Contra-assets (accumulated depreciation / amortization)",
    "They sit on the asset side but work like liabilities: depreciation goes on the CREDIT side. Net book value = cost − accumulated depreciation.",
    "Land is NEVER depreciated.",
    "# P&L (profit for the period)",
    "This is a temporary owners' equity account. Revenues and gains go on the credit side. Expenses and losses (COGS, salaries, rent used up, depreciation, interest, tax) go on the debit side.",
    "At the end: closing entry CE = Dr P&L / Cr Retained profits for the net profit. Use # 'CE' so the Income Statement check can ignore it.",
    "# Frequent traps",
    "A sale is TWO entries: (a) Dr Cash/A/R, Cr P&L (revenue) and (b) Dr P&L (COGS), Cr Inventory.",
    "Prepaid rent: paying for it is an asset (Dr Prepaid, Cr Cash). Only the part used up in the period is an expense (Dr P&L, Cr Prepaid).",
    "Cash received before delivery is a liability: Deposits from customers.",
    "Buying on credit: Cr Accounts payable, not Cash. Paying later: Dr A/P, Cr Cash, with NO expense.",
    "Accrued interest, salaries and tax not yet paid: Dr P&L, Cr Interest/Salaries/Taxes payable.",
    "A loan repayment only reduces the loan (Dr Loan, Cr Cash). The interest part is an expense.",
    "A purchase financed by the seller or a mortgage: Dr Land/Building, Cr Mortgage/Obligations (and Cr Cash for any down payment).",
    "Dividends: Dr Retained profits, Cr Cash. They are never a P&L expense.",
    "Share issue above par: Cr Share capital (par × shares) + Cr Share premium (the rest).",
    "# Checks",
    "Below the T-accounts: total debits must equal total credits. On the Balance Sheet sheet: A = L + OE.",
])
t.freeze_panes = f"A{TOP - 1}"

# =====================================================================
# 3. JOURNAL
# =====================================================================
lists = wb.create_sheet("Lists")
all_keys = [k for pair in ASSETS for k, _, _ in pair] + [k for pair in LOE for k, _, _ in pair]
for i, k in enumerate(all_keys, 1):
    lists[f"A{i}"] = f"={ACC[k]['title']}"
N_ACC = len(all_keys)
for i, e in enumerate(["A+", "A−", "L+", "L−", "OE+", "OE−", "Rev (OE+)", "Exp (OE−)", "Contra-A+", "Contra-A−"], 1):
    lists[f"B{i}"] = e
for i, e in enumerate(["O", "I", "F", "Non-cash"], 1):
    lists[f"C{i}"] = e
lists.sheet_state = "hidden"

j = wb.create_sheet("Journal", 1)
j.sheet_view.showGridLines = False
for col, w in zip("ABCDEFGHIJ", [2, 7, 40, 36, 13, 13, 11, 11, 11, 2]):
    j.column_dimensions[col].width = w
merge(j, "B1:I1", "JOURNAL ENTRIES", bg="404040", color="FFFFFF", size=14)
put(j, "B2", "Company:", bold=True); j.merge_cells("C2:D2"); put(j, "C2", f"={COMPANY}")
put(j, "E2", "Period:", bold=True); j.merge_cells("F2:G2"); put(j, "F2", f"={PERIOD}")
heads = ["#", "Description of transaction", "Account (pick from list or type)", "Dr", "Cr", "Effect", "Cash flow", "Entry check"]
J_FIRST, J_LAST = 7, 106
put(j, "C4", "TOTAL", bold=True, align="right")
put(j, "E4", f"=SUM(E{J_FIRST}:E{J_LAST})", bold=True, num=NUM)
put(j, "F4", f"=SUM(F{J_FIRST}:F{J_LAST})", bold=True, num=NUM)
put(j, "G4", check_formula(f"E4-F4"), bold=True, align="center")
j.merge_cells("G4:H4")
add_ok_format(j, "G4")
for i, h in enumerate(heads):
    put(j, f"{'BCDEFGHI'[i]}{J_FIRST - 1}", h, bold=True, color="FFFFFF", bg="595959", align="center")
for rr in range(J_FIRST, J_LAST + 1):
    for col in "BCDEFGH":
        put(j, f"{col}{rr}", color=INPUT_BLUE, num=NUM if col in "EF" else None,
            align="center" if col in "BGH" else None, border=Border(bottom=hair),
            bg="F7F7F7" if rr % 2 else None)
    put(j, f"I{rr}", f'=IF(B{rr}="","",IF(ABS(SUMIF($B${J_FIRST}:$B${J_LAST},B{rr},$E${J_FIRST}:$E${J_LAST})-SUMIF($B${J_FIRST}:$B${J_LAST},B{rr},$F${J_FIRST}:$F${J_LAST}))<0.5,"OK","ERROR: Dr≠Cr"))',
        align="center", border=Border(bottom=hair), size=9)
add_ok_format(j, f"I{J_FIRST}:I{J_LAST}")
dv = DataValidation(type="list", formula1=f"=Lists!$A$1:$A${N_ACC}", allow_blank=True, showErrorMessage=False)
dv2 = DataValidation(type="list", formula1="=Lists!$B$1:$B$10", allow_blank=True, showErrorMessage=False)
dv3 = DataValidation(type="list", formula1="=Lists!$C$1:$C$4", allow_blank=True, showErrorMessage=False)
j.add_data_validation(dv); j.add_data_validation(dv2); j.add_data_validation(dv3)
dv.add(f"D{J_FIRST}:D{J_LAST}"); dv2.add(f"G{J_FIRST}:G{J_LAST}"); dv3.add(f"H{J_FIRST}:H{J_LAST}")
j.freeze_panes = f"A{J_FIRST}"
notes(j, "K", J_FIRST - 1, [
    "# How to use",
    "One line per account touched. All lines of the same transaction share the same # (e.g. 3a, 3a).",
    "Write the debit lines first, then the credit lines (Dr Cash / Cr Loan).",
    "For P&L lines, write e.g. 'P&L – Sales revenue' or 'P&L – Salaries expense' so the Income Statement is easy to build.",
    "Effect column: A+/A−/L+/L−/OE+/OE−, as in the course notes. It forces you to think about which side each line goes on.",
    "Cash flow column: only for lines that touch CASH. O = operating, I = investing, F = financing.",
    "Entry check turns green when that # balances (debits = credits).",
    "# Rule of thumb",
    "Debits: asset ↑, expense ↑, liability ↓, OE ↓",
    "Credits: asset ↓, revenue ↑, liability ↑, OE ↑",
    "# Hint",
    "Record everything in the Journal first, then post to the T-Accounts. Mistakes are much easier to spot here than in the Ts.",
], width=70)

# =====================================================================
# 4. BALANCE SHEET
# =====================================================================
b = wb.create_sheet("Balance Sheet")
b.sheet_view.showGridLines = False
for col, w in zip("ABCDEFG", [2, 44, 15, 15, 15, 3, 70]):
    b.column_dimensions[col].width = w
merge(b, "B1:E1", "BALANCE SHEET  (statement of financial position)", bg="404040", color="FFFFFF", size=14)
put(b, "B2", f'={COMPANY}&" – "&{PERIOD}&"  (in "&{CUR}&")"', italic=True)
for i, h in enumerate(["", "Beginning (BB)", "Ending (EB)", "Change (Δ)"]):
    put(b, f"{'BCDE'[i]}4", h, bold=True, align="center", bg=GREY, border=Border(bottom=thin))
BS = {}
r = 5

def section(label, bg, color="FFFFFF"):
    global r
    merge(b, f"B{r}:E{r}", label, bg=bg, color=color, align="left"); r += 1

def line(key, sign=1, indent=1):
    global r
    a = ACC[key]
    put(b, f"B{r}", f'="{"   " * indent}"&{a["title"]}' if sign == 1 else f'="{"   " * indent}Less: "&{a["title"]}')
    s = "" if sign == 1 else "-"
    put(b, f"C{r}", f"={s}{a['bb']}", num=NUM)
    put(b, f"D{r}", f"={s}{a['eb']}", num=NUM)
    put(b, f"E{r}", f"=D{r}-C{r}", num=NUM, color="595959")
    BS[key] = r; r += 1

def subtotal(label, rows, key, bg, bold=True, top=thin):
    global r
    put(b, f"B{r}", label, bold=bold, bg=bg)
    for col in "CDE":
        put(b, f"{col}{r}", "=" + "+".join(f"{col}{x}" for x in rows) if rows else 0, bold=bold, num=NUM, bg=bg, border=Border(top=top))
    BS[key] = r; r += 1

section("ASSETS  (uses of capital)", A_DARK)
put(b, f"B{r}", "Current assets", bold=True, bg=A_LIGHT); [put(b, f"{c}{r}", bg=A_LIGHT) for c in "CDE"]; r += 1
ca_start = r
for k in ["cash", "mktsec", "ar", "inv", "prepaid", "other_ca"]: line(k)
subtotal("Total current assets (CA)", list(range(ca_start, r)), "tca", A_LIGHT)
put(b, f"B{r}", "Non-current assets", bold=True, bg=A_LIGHT); [put(b, f"{c}{r}", bg=A_LIGHT) for c in "CDE"]; r += 1
nca_rows = []
line("land"); nca_rows.append(BS["land"])
line("bldg"); line("ad_bldg", -1, 2)
subtotal("      Buildings, net", [BS["bldg"], BS["ad_bldg"]], "bldg_net", None, bold=False); nca_rows.append(BS["bldg_net"])
line("fe"); line("ad_fe", -1, 2)
subtotal("      Furniture & equipment, net", [BS["fe"], BS["ad_fe"]], "fe_net", None, bold=False); nca_rows.append(BS["fe_net"])
line("sw"); line("am_sw", -1, 2)
subtotal("      Intangible assets, net", [BS["sw"], BS["am_sw"]], "sw_net", None, bold=False); nca_rows.append(BS["sw_net"])
line("fininv"); nca_rows.append(BS["fininv"])
subtotal("Total non-current assets (NCA)", nca_rows, "tnca", A_LIGHT)
subtotal("TOTAL ASSETS", [BS["tca"], BS["tnca"]], "ta", A_DARK, top=med)
for c in "BCDE": b[f"{c}{BS['ta']}"].font = font(True, "FFFFFF")
r += 1
section("OWNERS' EQUITY & LIABILITIES  (sources of capital)", L_DARK)
put(b, f"B{r}", "Owners' equity", bold=True, bg=OE_LIGHT); [put(b, f"{c}{r}", bg=OE_LIGHT) for c in "CDE"]; r += 1
oe_start = r
for k in ["sc", "sp", "rp", "pl"]: line(k)
subtotal("Total owners' equity (OE)", list(range(oe_start, r)), "toe", OE_LIGHT)
put(b, f"B{r}", "Non-current liabilities", bold=True, bg=L_LIGHT); [put(b, f"{c}{r}", bg=L_LIGHT) for c in "CDE"]; r += 1
ncl_start = r
for k in ["ltloan", "mort"]: line(k)
subtotal("Total non-current liabilities (NCL)", list(range(ncl_start, r)), "tncl", L_LIGHT)
put(b, f"B{r}", "Current liabilities", bold=True, bg=L_LIGHT); [put(b, f"{c}{r}", bg=L_LIGHT) for c in "CDE"]; r += 1
cl_start = r
for k in ["ap", "salp", "intp", "taxp", "dep", "divp", "stloan", "other_l"]: line(k)
subtotal("Total current liabilities (CL)", list(range(cl_start, r)), "tcl", L_LIGHT)
subtotal("Total liabilities (L)", [BS["tncl"], BS["tcl"]], "tl", L_LIGHT)
subtotal("TOTAL OWNERS' EQUITY & LIABILITIES", [BS["toe"], BS["tl"]], "tloe", L_DARK, top=med)
for c in "BCDE": b[f"{c}{BS['tloe']}"].font = font(True, "FFFFFF")
r += 1
put(b, f"B{r}", "CHECK: Assets = Liabilities + Owners' equity", bold=True, bg=GREY)
put(b, f"C{r}", check_formula(f"C{BS['ta']}-C{BS['tloe']}"), bold=True, align="center")
put(b, f"D{r}", check_formula(f"D{BS['ta']}-D{BS['tloe']}"), bold=True, align="center")
add_ok_format(b, f"C{r}:D{r}")
BS["check"] = r; r += 1
put(b, f"B{r}", "CHECK: T-accounts debits = credits", bold=True, bg=GREY)
put(b, f"D{r}", f"={T_CHECK}", bold=True, align="center"); add_ok_format(b, f"D{r}"); r += 2
put(b, f"B{r}", "Key figures", bold=True, bg=GREY); [put(b, f"{c}{r}", bg=GREY) for c in "CDE"]; r += 1
put(b, f"B{r}", "   Working capital (CA − CL)")
for col in "CD": put(b, f"{col}{r}", f"={col}{BS['tca']}-{col}{BS['tcl']}", num=NUM)
r += 1
put(b, f"B{r}", "   Net assets (A − L) = OE")
for col in "CD": put(b, f"{col}{r}", f"={col}{BS['ta']}-{col}{BS['tl']}", num=NUM)
r += 1
put(b, f"B{r}", "   Debt-to-equity (L / OE)")
for col in "CD": put(b, f"{col}{r}", f'=IF({col}{BS["toe"]}=0,"-",{col}{BS["tl"]}/{col}{BS["toe"]})', num="0.00x")
r += 1
put(b, f"B{r}", "   Current ratio (CA / CL)")
for col in "CD": put(b, f"{col}{r}", f'=IF({col}{BS["tcl"]}=0,"-",{col}{BS["tca"]}/{col}{BS["tcl"]})', num="0.00x")
notes(b, "G", 4, [
    "# This sheet is 100% formulas",
    "Everything comes from the T-Accounts sheet: Beginning = BB row, Ending = EB row. Don't type here. If a number is wrong, fix the T-account.",
    "Account names come from the T-account titles, so renaming a T renames the line here.",
    "# Classification (CN-231-E)",
    "Current = cash, or turned into cash / sold / used up within 12 months or the operating cycle, whichever is longer.",
    "Cash & cash equivalents: cash + investments maturing in under 3 months.",
    "Marketable securities: 3 to 12 months (current). Longer = financial investments (non-current).",
    "Current portion of a long-term loan (next repayment) goes in current liabilities.",
    "PPE and intangibles are shown at cost less accumulated depreciation/amortization. Land is not depreciated.",
    "# Profit for the period line",
    "Shows 0 once you have recorded the closing entry (net profit moved into Retained profits). If you have not, the net profit shows here. The total is correct either way.",
    "# Presentation",
    "This layout is the stakeholder view (A = L + OE). Continental Europe shows NCA first. UK/Ireland uses net assets (NCA + CA − CL − NCL = OE). The numbers are the same in all three.",
    "# Checks",
    "Both check cells must be green in BOTH columns. If only Ending fails, a transaction is posted on one side only.",
])
b.freeze_panes = "A5"

# =====================================================================
# 5. INCOME STATEMENT
# =====================================================================
s = wb.create_sheet("Income Statement")
s.sheet_view.showGridLines = False
for col, w in zip("ABCDEF", [2, 52, 16, 12, 3, 70]):
    s.column_dimensions[col].width = w
merge(s, "B1:D1", "INCOME STATEMENT  (P&L)", bg=IS_DARK, color="FFFFFF", size=14)
put(s, "B2", f'={COMPANY}&" – for the period "&{PERIOD}&"  (in "&{CUR}&")"', italic=True)
put(s, "C4", "Amount", bold=True, align="center", bg=GREY, border=Border(bottom=thin))
put(s, "D4", "% of sales", bold=True, align="center", bg=GREY, border=Border(bottom=thin))
IS = {}
r = 5
def is_in(key, label):
    global r
    put(s, f"B{r}", label)
    put(s, f"C{r}", None, color=INPUT_BLUE, num=NUM, border=Border(bottom=hair))
    IS[key] = r; r += 1
def is_tot(key, label, rows, dark=False):
    global r
    bg = IS_DARK if dark else IS_LIGHT
    fc = "FFFFFF" if dark else "000000"
    put(s, f"B{r}", label, bold=True, bg=bg, color=fc)
    put(s, f"C{r}", "=" + "+".join(f"C{x}" for x in rows), bold=True, num=NUM, bg=bg, color=fc, border=Border(top=thin))
    put(s, f"D{r}", bg=bg)
    IS[key] = r; r += 1

is_in("sales", "Sales revenue")
is_in("cogs", "− Cost of goods sold (COGS)")
is_tot("gp", "= Gross profit (margin)", [IS["sales"], IS["cogs"]])
op_start = r
is_in("mkt", "− Marketing & selling expenses")
is_in("adm", "− Administration expenses")
is_in("rd", "− Research & development expenses")
is_in("sal", "− Salaries expense (if not split by function)")
is_in("rent", "− Rent expense")
is_in("dep", "− Depreciation & amortization expense")
is_in("oox", "− Other operating expenses (utilities, etc.)")
is_in("nonrec", "+/− Other non-recurring operating items (e.g. gain/loss on sale of PPE)")
is_tot("ebit", "= Operating profit (EBIT)", [IS["gp"]] + list(range(op_start, r)))
is_in("finc", "+ Financial income")
is_in("finx", "− Financial expenses (interest)")
is_tot("pbt", "= Profit before tax", [IS["ebit"], IS["finc"], IS["finx"]])
is_in("tax", "− Tax expense")
is_tot("npc", "= Net profit from continuing operations", [IS["pbt"], IS["tax"]])
is_in("disc", "+/− Profit (loss) from discontinued operations")
is_tot("np", "= NET PROFIT", [IS["npc"], IS["disc"]], dark=True)
is_in("mi", "− Profit for minority (non-controlling) interests")
is_tot("npp", "= Net profit for parent company owners", [IS["np"], IS["mi"]])
for key in ["sales", "cogs", "gp", "mkt", "adm", "rd", "sal", "rent", "dep", "oox", "nonrec", "ebit", "finc", "finx", "pbt", "tax", "npc", "disc", "np", "mi", "npp"]:
    rr = IS[key]
    s[f"D{rr}"].value = f'=IF(OR($C${IS["sales"]}=0,C{rr}=""),"",C{rr}/$C${IS["sales"]})'
    s[f"D{rr}"].number_format = PCT
    s[f"D{rr}"].font = font(key in ("gp", "ebit", "pbt", "npc", "np", "npp"), "FFFFFF" if key == "np" else "595959", 9)
    s[f"D{rr}"].alignment = Alignment(horizontal="center")
r += 1
put(s, f"B{r}", "Memo items (used by the indirect cash flow)", bold=True, bg=GREY); put(s, f"C{r}", bg=GREY); put(s, f"D{r}", bg=GREY); r += 1
put(s, f"B{r}", "Total depreciation & amortization included above (positive)")
put(s, f"C{r}", f"=-C{IS['dep']}", num=NUM)
IS["memo_da"] = r; r += 1
put(s, f"B{r}", "Gain (+) / loss (−) on sale of non-current assets included above")
put(s, f"C{r}", None, color=INPUT_BLUE, num=NUM, border=Border(bottom=hair))
IS["memo_gain"] = r; r += 2

# check vs P&L T-account (ignores closing entry lines tagged CE)
pl = ACC["pl"]
pl_net = (f"(SUM({pl['cr_rng']})-SUMIF({pl['refr_rng']},\"CE\",{pl['cr_rng']}))"
          f"-(SUM({pl['dr_rng']})-SUMIF({pl['refl_rng']},\"CE\",{pl['dr_rng']}))")
put(s, f"B{r}", "Net profit according to the P&L T-account (excl. CE)", bold=True, bg=GREY)
put(s, f"C{r}", f"={pl_net}", num=NUM, bold=True); IS["pl_t"] = r; r += 1
put(s, f"B{r}", "CHECK: Income statement = P&L T-account", bold=True, bg=GREY)
put(s, f"C{r}", check_formula(f"C{IS['np']}-C{IS['pl_t']}"), bold=True, align="center")
add_ok_format(s, f"C{r}"); IS["check"] = r; r += 1

notes(s, "F", 4, [
    "# Sign convention",
    "Type revenues and gains as POSITIVE and expenses and losses as NEGATIVE (e.g. COGS −781), as in the course notes. Subtotals simply add up.",
    "# Where the numbers come from",
    "Every line is one of the entries on the P&L T-account: credits are revenues, debits are expenses.",
    "Only use the lines the case needs and leave the rest empty (they show '-').",
    "# Format (CN-232-E)",
    "By function (Table 1): COGS, marketing & selling, administration, R&D.",
    "By nature (Table 2): materials, personnel/salaries, depreciation, other.",
    "Homework cases often mix the two (like DSJ: salaries, rent, depreciation, other opex). That's why both kinds of line are here. Never put the same cost on two lines.",
    "# Classic mistakes",
    "Revenue is recognised on DELIVERY, not when cash is received. Customer deposits are a liability, not revenue.",
    "COGS is the cost of the units SOLD, not of the units purchased.",
    "Only the part of prepaid rent used up in the period is an expense.",
    "Interest expense accrues with time, whether or not it is paid.",
    "Loan principal repayments, dividends and asset purchases are NOT expenses.",
    "A gain or loss on selling PPE = price − book value. It goes in 'non-recurring items', not in sales.",
    "Tax expense = tax rate × profit before tax (unless the case says otherwise).",
    "# Memo items",
    "D&A is filled in from the depreciation line. If depreciation is hidden inside COGS/SG&A, type the total over the formula.",
    "Gain/loss on sale: type it here as well so the indirect cash flow can remove it.",
    "# Check",
    "Compares net profit with the balance of the P&L T-account. Lines tagged # 'CE' (the closing entry) are ignored.",
])
s.freeze_panes = "A5"

# =====================================================================
# 6. CASH FLOW STATEMENT
# =====================================================================
c = wb.create_sheet("Cash Flow")
c.sheet_view.showGridLines = False
for col, w in zip("ABCDEF", [2, 56, 16, 12, 3, 70]):
    c.column_dimensions[col].width = w
merge(c, "B1:C1", "STATEMENT OF CASH FLOWS", bg=CF_DARK, color="FFFFFF", size=14)
put(c, "B2", f'={COMPANY}&" – for the period "&{PERIOD}&"  (in "&{CUR}&")"', italic=True)
CF = {}
r = 4
merge(c, f"B{r}:C{r}", "A) DIRECT METHOD  (list of cash movements; + collections / − payments)", bg="404040", color="FFFFFF", align="left"); r += 1

def cf_head(label, bg):
    global r
    put(c, f"B{r}", label, bold=True, bg=bg); put(c, f"C{r}", bg=bg); r += 1
def cf_in(key, label):
    global r
    put(c, f"B{r}", label)
    put(c, f"C{r}", None, color=INPUT_BLUE, num=NUM, border=Border(bottom=hair))
    CF[key] = r; r += 1
def cf_tot(key, label, rows, bg, fc="000000"):
    global r
    put(c, f"B{r}", label, bold=True, bg=bg, color=fc)
    put(c, f"C{r}", "=" + "+".join(f"C{x}" for x in rows), bold=True, num=NUM, bg=bg, color=fc, border=Border(top=thin))
    CF[key] = r; r += 1

cf_head("Operating activities", CFO_L); s0 = r
cf_in("coll", "+ Collections from customers (incl. customer deposits)")
cf_in("othin", "+ Interest / dividends received")
cf_in("supp", "− Payments to suppliers")
cf_in("emp", "− Payments to employees")
cf_in("rentp", "− Payments for rent (incl. prepaid rent)")
cf_in("oopp", "− Payments for other operating expenses (utilities, etc.)")
cf_in("intp", "− Payments for interest")
cf_in("taxp", "− Payments for taxes")
cf_tot("cfo", "= Cash flow from operating activities (CFO)", list(range(s0, r)), CFO_L)
r += 1
cf_head("Investing activities", CFI_L); s0 = r
cf_in("land", "− Purchase of land")
cf_in("ppe", "− Purchase of buildings, property & equipment")
cf_in("intang", "− Purchase of intangible assets (software, patents)")
cf_in("sh", "− Investment in shares / marketable securities")
cf_in("sppe", "+ Sale of property, plant & equipment")
cf_in("ssh", "+ Sale of shares / marketable securities")
cf_tot("cfi", "= Cash flow from (used in) investing activities (CFI)", list(range(s0, r)), CFI_L)
r += 1
cf_head("Financing activities", CFF_L); s0 = r
cf_in("eq", "+ Issue of share capital (incl. share premium)")
cf_in("newl", "+ New loans / mortgages received")
cf_in("repl", "− Loan & mortgage repayments (principal only)")
cf_in("div", "− Dividends paid")
cf_tot("cff", "= Cash flow from (used in) financing activities (CFF)", list(range(s0, r)), CFF_L)
r += 1
cf_tot("dcash", "CHANGE IN CASH (CFO + CFI + CFF)", [CF["cfo"], CF["cfi"], CF["cff"]], CF_DARK, "FFFFFF")
put(c, f"B{r}", "Cash, beginning balance"); put(c, f"C{r}", f"='Balance Sheet'!C{BS['cash']}", num=NUM); CF["cbb"] = r; r += 1
put(c, f"B{r}", "Change in cash during the period"); put(c, f"C{r}", f"=C{CF['dcash']}", num=NUM); r += 1
put(c, f"B{r}", "Cash, ending balance", bold=True); put(c, f"C{r}", f"=C{CF['cbb']}+C{CF['dcash']}", num=NUM, bold=True, border=Border(top=thin, bottom=Side(style="double"))); CF["ceb"] = r; r += 1
put(c, f"B{r}", "CHECK: ending cash = Balance Sheet cash", bold=True, bg=GREY)
put(c, f"C{r}", check_formula(f"C{CF['ceb']}-'Balance Sheet'!D{BS['cash']}"), bold=True, align="center"); add_ok_format(c, f"C{r}"); CF["chk1"] = r; r += 1
put(c, f"B{r}", "Free cash flow (CFO + CFI, as in the course example)"); put(c, f"C{r}", f"=C{CF['cfo']}+C{CF['cfi']}", num=NUM); r += 2

merge(c, f"B{r}:C{r}", "B) INDIRECT METHOD for CFO  (net profit ± adjustments; automatic)", bg="404040", color="FFFFFF", align="left"); r += 1
cf_head("Operating activities", CFO_L); s0 = r
def cf_f(key, label, formula):
    global r
    put(c, f"B{r}", label); put(c, f"C{r}", formula, num=NUM); CF[key] = r; r += 1
cf_f("i_np", "Net profit", f"='Income Statement'!C{IS['np']}")
cf_f("i_da", "+ Depreciation & amortization", f"='Income Statement'!C{IS['memo_da']}")
cf_f("i_gl", "− Gains / + losses on sale of non-current assets", f"=-'Income Statement'!C{IS['memo_gain']}")
for k, lab in [("ar", "− Increase / + decrease in accounts receivable"), ("inv", "− Increase / + decrease in inventories"),
               ("prepaid", "− Increase / + decrease in prepaid expenses"), ("other_ca", "− Increase / + decrease in other current assets")]:
    cf_f("i_" + k, lab, f"=-'Balance Sheet'!E{BS[k]}")
for k, lab in [("ap", "+ Increase / − decrease in accounts payable"), ("salp", "+ Increase / − decrease in salaries payable"),
               ("intp", "+ Increase / − decrease in interest payable"), ("taxp", "+ Increase / − decrease in taxes payable"),
               ("dep", "+ Increase / − decrease in deposits from customers")]:
    cf_f("i_" + k, lab, f"='Balance Sheet'!E{BS[k]}")
cf_tot("i_cfo", "= CFO (indirect method)", list(range(s0, r)), CFO_L)
put(c, f"B{r}", "CHECK: CFO indirect = CFO direct", bold=True, bg=GREY)
put(c, f"C{r}", check_formula(f"C{CF['i_cfo']}-C{CF['cfo']}"), bold=True, align="center"); add_ok_format(c, f"C{r}"); CF["chk2"] = r; r += 1
put(c, f"B{r}", "CHECK: CFO + CFI + CFF = ΔCash on the Balance Sheet", bold=True, bg=GREY)
put(c, f"C{r}", check_formula(f"C{CF['i_cfo']}+C{CF['cfi']}+C{CF['cff']}-'Balance Sheet'!E{BS['cash']}"), bold=True, align="center"); add_ok_format(c, f"C{r}"); CF["chk3"] = r; r += 1

notes(c, "F", 4, [
    "# Sign convention (CN-233-E)",
    "Cash collections are positive and cash payments negative. Type −20,000 for a payment.",
    "# Direct method: where the numbers come from",
    "Go through the CASH T-account line by line. Every debit is a collection and every credit is a payment. Tag each one O, I or F.",
    "Only CASH moves go here. Depreciation, purchases on credit, accruals and gains/losses never do.",
    "# Classification",
    "Operating: customers, suppliers, employees, rent, utilities, INTEREST paid and TAXES paid.",
    "Investing: buying/selling land, buildings, equipment, software, shares of other companies.",
    "Financing: share issues, new loans, repaying loan/mortgage PRINCIPAL, dividends paid.",
    "A mortgage/loan repayment is FINANCING (principal). Its interest is OPERATING.",
    "Paying a seller later for a building/land bought on credit is an investing outflow when paid.",
    "Selling PPE: the whole cash received goes in CFI. The gain/loss is only an adjustment in the indirect CFO.",
    "Marketable securities maturing in under 3 months are cash equivalents, so there is no cash flow line.",
    "# Indirect method (automatic)",
    "Starts from net profit and uses the Balance Sheet changes (Δ = EB − BB). Assets: minus the increase. Liabilities: plus the increase.",
    "It only matches the direct method if the Income Statement memo items (D&A, gain/loss) are filled in.",
    "Dividends payable, loans and mortgages are NOT operating liabilities, so they are left out on purpose.",
    "# Checks",
    "1) Ending cash = Balance Sheet cash.  2) Indirect CFO = direct CFO.  3) The three flows explain the change in cash.",
    "If check 2 fails, open the CF Worksheet sheet to find the account that isn't explained.",
])
c.freeze_panes = "A4"

# =====================================================================
# 7. CF WORKSHEET  (spreadsheet approach of CN-233-E)
# =====================================================================
w = wb.create_sheet("CF Worksheet")
w.sheet_view.showGridLines = False
for col, wd in zip("ABCDEFGHIJK", [2, 40, 14, 13, 13, 13, 13, 40, 3, 70, 2]):
    w.column_dimensions[col].width = wd
merge(w, "B1:H1", "CASH FLOW WORKSHEET   ΔCash = −ΔAssets other than cash + ΔL + ΔOE", bg=CF_DARK, color="FFFFFF", size=13)
put(w, "B2", f'={COMPANY}&" – "&{PERIOD}', italic=True)
hdr = ["Balance sheet account", "Change (sign-adjusted)", "CFO\n(net profit ± adj.)", "CFI\n(cash only)", "CFF\n(cash only)", "Unexplained\n(must be 0)", "Explanation (e.g. dep 54 + loss 7)"]
for i, h in enumerate(hdr):
    bg = {2: CFO_L, 3: CFI_L, 4: CFF_L}.get(i, GREY)
    put(w, f"{'BCDEFGH'[i]}4", h, bold=True, bg=bg, align="center", wrap=True, border=Border(bottom=thin))
w.row_dimensions[4].height = 30
r = 5
W_ROWS = []
def w_line(key, sign, header=None):
    global r
    a = ACC[key]
    prefix = "−Δ " if sign == -1 else "+Δ "
    put(w, f"B{r}", f'="{prefix}"&{a["title"]}')
    put(w, f"C{r}", f"={'-' if sign == -1 else ''}'Balance Sheet'!E{BS[key]}", num=NUM)
    for col in "DEF":
        put(w, f"{col}{r}", None, color=INPUT_BLUE, num=NUM, border=Border(bottom=hair))
    put(w, f"G{r}", f"=C{r}-SUM(D{r}:F{r})", num=NUM)
    put(w, f"H{r}", None, color=INPUT_BLUE, size=9, border=Border(bottom=hair))
    W_ROWS.append(r); r += 1
def w_head(label, bg, fc="000000"):
    global r
    merge(w, f"B{r}:H{r}", label, bg=bg, color=fc, align="left"); r += 1

w_head("Assets other than cash  (reverse the sign: an increase uses cash)", A_LIGHT)
for k in ["mktsec", "ar", "inv", "prepaid", "other_ca", "land", "bldg", "fe", "sw", "fininv"]:
    w_line(k, -1)
w_head("Contra-assets  (accumulated depreciation lowers assets, so it is added back)", A_LIGHT)
for k in ["ad_bldg", "ad_fe", "am_sw"]:
    w_line(k, +1)
w_head("Liabilities", L_LIGHT)
for k in ["ap", "salp", "intp", "taxp", "dep", "divp", "stloan", "other_l", "ltloan", "mort"]:
    w_line(k, +1)
w_head("Owners' equity", OE_LIGHT)
for k in ["sc", "sp", "rp", "pl"]:
    w_line(k, +1)
first, last = W_ROWS[0], W_ROWS[-1]
put(w, f"B{r}", "TOTALS  = ΔCash  |  CFO  |  CFI  |  CFF", bold=True, bg=CF_DARK, color="FFFFFF")
for col in "CDEFG":
    put(w, f"{col}{r}", f"=SUM({col}{first}:{col}{last})", bold=True, num=NUM, bg=CF_DARK, color="FFFFFF", border=Border(top=med))
put(w, f"H{r}", bg=CF_DARK); tr = r; r += 2
put(w, f"B{r}", "CHECK: total change = ΔCash on the Balance Sheet", bold=True, bg=GREY)
put(w, f"C{r}", check_formula(f"C{tr}-'Balance Sheet'!E{BS['cash']}"), bold=True, align="center"); add_ok_format(w, f"C{r}"); r += 1
put(w, f"B{r}", "CHECK: every change explained", bold=True, bg=GREY)
put(w, f"C{r}", f'=IF(SUMPRODUCT(ABS(G{first}:G{last}))<0.5,"OK","ERROR: "&TEXT(SUMPRODUCT(ABS(G{first}:G{last})),"#,##0"))', bold=True, align="center"); add_ok_format(w, f"C{r}"); r += 1
put(w, f"B{r}", "CHECK: CFO / CFI / CFF = Cash Flow sheet", bold=True, bg=GREY)
put(w, f"C{r}", check_formula(f"ABS(D{tr}-'Cash Flow'!C{CF['cfo']})+ABS(E{tr}-'Cash Flow'!C{CF['cfi']})+ABS(F{tr}-'Cash Flow'!C{CF['cff']})"), bold=True, align="center"); add_ok_format(w, f"C{r}"); r += 1
add_ok_format(w, f"G{first}:G{last}")
w.conditional_formatting.add(f"G{first}:G{last}", FormulaRule(formula=[f"ABS(G{first})>=0.5"], fill=fill("FFC7CE")))
notes(w, "J", 4, [
    "# What this is",
    "The course's spreadsheet approach (CN-233-E, p. 4–8). Explain the change in every non-cash account and you have explained the change in cash.",
    "Optional, but it's the best way to find a mistake in the indirect method.",
    "# How to fill",
    "Column C is automatic. Split it into CFO / CFI / CFF so that 'Unexplained' becomes 0.",
    "CFI and CFF: only real cash flows (purchase of PPE, loan repaid, dividends paid…).",
    "CFO: net profit and non-cash adjustments (depreciation, losses, changes in working capital).",
    "Several items in one cell: type a formula, e.g. =54+7, and write the story in column H.",
    "# Course example (ABC Co.)",
    "PPE net −6 = +54 depreciation (CFO) +7 loss on sale (CFO) −72 purchase (CFI) +5 sale (CFI).",
    "Retained earnings +34 = +44 net profit (CFO) −10 dividends (CFF).",
    "Interest payable −2 → CFO.  Bank loan −31 → CFF.  New shares +15 → CFF.",
    "# Tips",
    "If you did not record the closing entry, net profit sits in the P&L row: put it in CFO there.",
    "If you use separate accumulated depreciation accounts, the depreciation goes on those rows (CFO) and the PPE-at-cost row only shows purchases and disposals.",
])
w.freeze_panes = "A5"

# ---- sheet order & tab colours ----
order = ["Guide", "Journal", "T-Accounts", "Balance Sheet", "Income Statement", "Cash Flow", "CF Worksheet", "Lists"]
wb._sheets = [wb[n] for n in order]
wb["Guide"].sheet_properties.tabColor = "404040"
wb["Journal"].sheet_properties.tabColor = "808080"
wb["T-Accounts"].sheet_properties.tabColor = A_DARK
wb["Balance Sheet"].sheet_properties.tabColor = L_DARK
wb["Income Statement"].sheet_properties.tabColor = IS_DARK
wb["Cash Flow"].sheet_properties.tabColor = CF_DARK
wb["CF Worksheet"].sheet_properties.tabColor = "AB47BC"
for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 100
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
wb.active = 0
wb.save(OUT)
print("saved", OUT)
