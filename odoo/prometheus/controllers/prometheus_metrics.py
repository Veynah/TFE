import logging
from prometheus_client import CollectorRegistry, Counter, Gauge, GaugeMetricFamily, generate_latest
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

TOKEN = "KS&nxAvEqSeMtHHivnB7aBZTQAqDUWdBlfBFkLXBN35SguXD3mHo*wyxQf@%tdH##qkmsXZoVK5D8e9Y7y5t*g%&%Bt3SZMS7hX8GBMYdv*B8ntAqzzqhwF8jyeKQ^Cy"

class PrometheusController(http.Controller):
    @http.route(["/metrics"], auth="public", type="http", methods=["GET"])
    def metrics(self):
        """
        Provide Prometheus metrics.
        """

        auth_token = request.httprequest.headers.get("Authorization")
        if auth_token != f"Bearer {TOKEN}":
            _logger.warning("Access denied: invalid token")
            return http.Response("Unauthorized", status=403)
        registry = CollectorRegistry()

        for metric in request.env["ir.metric"].sudo().search([]):
            if metric.type == "gauge":
                g = Gauge(metric.name, metric.description, registry=registry)
                g.set(metric._get_value())
            if metric.type == "counter":
                c = Counter(metric.name, metric.description, registry=registry)
                c.inc(metric._get_value())
        collector = CustomCollector()
        registry.register(collector)
        return generate_latest(registry)

class CustomCollector:
    def collect(self):
        """
        Collector custom pour trouver les utilisateurs en ligne ainsi que leur nom
        """
        online_users = (
            request.env["bus.presence"].sudo().search([("status", "=", "online")])
        )

        online_users_count = GaugeMetricFamily(
            "odoo_online_users_total", "Number of online users"
        )
        online_users_count.add_metric([], len(online_users))

        online_user_status = GaugeMetricFamily(
            "odoo_online_user", "Online status of user", labels=["user"]
        )
        for user in online_users:
            online_user_status.add_metric([user.user_id.name], 1)

        yield online_users_count
        yield online_user_status
