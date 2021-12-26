from django.shortcuts import render
from django.http import Http404, HttpResponse
from pygments import highlight
from pygments.lexers import *
from pygments.formatters import HtmlFormatter
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import tempfile
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("highlightapp"),
    autoescape=select_autoescape()
)


rainbow = HtmlFormatter(style="rainbow_dash").get_style_defs(".highlight")
rainbow += ".highlight { background: white; }"


# Create your views here.

def index(request):
    return render(request, "highlight/index.html")

@require_http_methods(["GET", "POST"])
def highlightc(request, language=""):
    if request.method == "POST":
        # Get code
        code = request.POST.get("code")
        if not code:
            return HttpResponse(status=400)
        # Highlight
        highlighter = get_lexer_by_name(language)
        formatter = HtmlFormatter(linenos=True)
        result = highlight(code, highlighter, formatter)
        return render(request, "highlight/highlight.html", {
            "highlight": result
        })
    if not language:
        return HttpResponse(status=404)
    return render(request, "highlight/edit.html", {
        "language": language
    })

@require_http_methods(["GET", "POST"])
def topdf(request, language=""):
    font_config = FontConfiguration()
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
        fontcss = """
            pre {
                font-family: 'Cascadia Code', sans-serif;
            }
            code {
                font-family: 'Cascadia Code', sans-serif;
            }
        """
        font = CSS(string=fontcss, font_config=font_config)
        css = CSS(string=rainbow, font_config=font_config)
        html = HTML(string=htmlresult)
        pdfresult = html.write_pdf(presentational_hints=True, font_config=font_config, stylesheets=[css])
        # Create response headers
        response = HttpResponse(pdfresult, content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=code.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        # Send response
        return response
    return HttpResponse(status=200)
