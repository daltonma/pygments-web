"""
This file provides views for the Pygments Web App.
"""
import platform
supportsWeasyprint = True if platform.system() == "Linux" or platform.system() == "Darwin" else False
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from jinja2 import Environment, PackageLoader, select_autoescape
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.python import PythonLexer
from pygments.lexers.c_cpp import CLexer, CppLexer
from pygments.lexers.shell import BashLexer, BashSessionLexer, FishShellLexer
from pygments.lexers.html import HtmlLexer
from pygments.lexers.markup import MarkdownLexer
if supportsWeasyprint:
    from weasyprint import CSS, HTML
    from weasyprint.fonts import FontConfiguration
    from PyPDF2 import PdfReader, PdfWriter
    from io import BytesIO

env = Environment(
    loader=PackageLoader("highlightapp"),
    autoescape=select_autoescape()
)


rainbow = HtmlFormatter(style="rainbow_dash").get_style_defs(".highlight")
rainbow += ".highlight { background: white; }"


# Create your views here.

def index(request):
    """
    Index route.
    """
    return render(request, "highlight/index.html")


@require_http_methods(["GET", "POST"])
def highlightc(request, language=""):
    """
    This provides the editor interface and the syntax highlighter.
    """
    # If lexer not found ... return empty page
    try:
        highlighter = get_lexer_by_name(language)
    except Exception:
        return HttpResponse(status=404)
    if request.method == "POST":
        # Get code
        code = request.POST.get("code")
        
        title = request.POST.get("title")
        if not title:
            title = " "
        # Highlight
        # If lexer not found ... return empty page
        try:
            highlighter = get_lexer_by_name(language)
        except Exception:
            return HttpResponse(status=404)
        formatter = HtmlFormatter(linenos="inline")
        result = highlight(code, highlighter, formatter)
        # Return highlighted code
        return render(request, "highlight/highlight.html", {
            "highlight": result,
            "title": title
        })
    if not language:
        return HttpResponse(status=404)
    # Return Editor Page
    return render(request, "highlight/edit.html", {
        "language": language
    })


@require_http_methods(["GET", "POST"])
def topdf(request, language=""):
    """
    This method puts the highlighted code into a pdf.
    """
    if not supportsWeasyprint:
        return HttpResponse(status=404)
    font_config = FontConfiguration()
    if request.method == "POST":
        if not language:
            return HttpResponse(status=400)
        code = request.POST.get("code")
        if not code:
            return HttpResponse(status=400)
        title = request.POST.get("title")
        if not title:
            title = " "
        # Highlight
        # If lexer not found ... return empty page
        try:
            highlighter = get_lexer_by_name(language)
        except Exception:
            return HttpResponse(status=404)
        formatter = HtmlFormatter(linenos="inline")
        result = highlight(code, highlighter, formatter)
        # Render template
        template = env.get_template("highlight/topdf.html")
        htmlresult = template.render(highlight=result, title=title)
        # Pdf
        # Render CSS and HTML
        css = CSS(string=rainbow, font_config=font_config)
        html = HTML(string=htmlresult)
        # Write PDF
        pdfresult = html.write_pdf(
            presentational_hints=True, stylesheets=[css], font_config=font_config)
        # Set metadata
        pdf_reader = PdfReader(BytesIO(pdfresult))
        metadata = pdf_reader.metadata
        pdf_writer = PdfWriter()
        pdf_writer.append_pages_from_reader(pdf_reader)
        pdf_writer.add_metadata({
            '/Producer': 'Highlight by @bohrium2b',
            '/Title': title
        })
        with BytesIO() as finpdf:
            pdf_writer.write(finpdf)
            finpdf.seek(0)
            response = HttpResponse(finpdf, content_type='application/pdf;')
            response['Content-Disposition'] = 'inline; filename=code.pdf'
            response['Content-Transfer-Encoding'] = 'binary'
        # Create response headers
        
        # Send response
        return response
    return HttpResponse(status=200)
