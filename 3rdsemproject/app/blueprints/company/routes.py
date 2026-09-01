from flask import Blueprint, render_template

company_bp = Blueprint(
    "company",
    __name__,
    url_prefix="/company"
)


@company_bp.route("/register")
def register_page():
    return render_template("company/register.html")