"""
This file provides views for the Pygments Web App.
"""

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
from weasyprint import CSS, HTML

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
    if request.method == "POST":
        # Get code
        code = request.POST.get("code")
        if not code:
            return HttpResponse(status=400)
        # Highlight
        highlighter = get_lexer_by_name(language)
        formatter = HtmlFormatter(linenos=True)
        result = highlight(code, highlighter, formatter)
        # Return highlighted code
        return render(request, "highlight/highlight.html", {
            "highlight": result
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
    if request.method == "POST":
        if not language:
            return HttpResponse(status=400)
        code = request.POST.get("code")
        if not code:
            return HttpResponse(status=400)
        # Highlight
        highlighter = get_lexer_by_name(language)
        formatter = HtmlFormatter(linenos=True)
        result = highlight(code, highlighter, formatter)
        # Render template
        template = env.get_template("highlight/highlight.html")
        htmlresult = template.render(highlight=result)
        # Pdf
        css = CSS(string=rainbow)
        html = HTML(string=htmlresult)
        pdfresult = html.write_pdf(
            presentational_hints=True, stylesheets=[css])
        # Create response headers
        response = HttpResponse(pdfresult, content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=code.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        # Send response
        return response
    return HttpResponse(status=200)
