from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import FileResponse, HttpResponse


def html_to_pdf_response(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    buffer = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), buffer)
    if not pdf.err:
        buffer.seek(0)
        return  FileResponse(buffer, as_attachment=True, filename='fee-receipt.pdf')
    return HttpResponse('Something went wrong. Please contact admin.', status=500)


def html_to_pdf_buffer(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    buffer = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), buffer)
    if not pdf.err:
        buffer.seek(0)
        return buffer
    return None