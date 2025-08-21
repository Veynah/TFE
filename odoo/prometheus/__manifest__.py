{
    "name": "Prometheus",
    "summary": """
        Monitor Odoo metrics with Prometheus.
    """,
    "category": "Technical",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mail", "resource"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_metric.xml",
        "views/ir_metric.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "external_dependencies": {"python": ["prometheus_client"]},
}
