import io

from openpyxl import Workbook

def start(headers, query_result):
    wb = Workbook()
    ws = wb.active
    ws.append(headers)

    for row in query_result:
        if row:
            ws.append(row)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()