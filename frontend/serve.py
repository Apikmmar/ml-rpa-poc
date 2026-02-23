from http.server import HTTPServer, SimpleHTTPRequestHandler

ROUTES = {
    "/":                            "/pages/index.html",
    "/index":                       "/pages/index.html",
    "/orders":                      "/pages/orders/index.html",
    "/orders/list":                 "/pages/orders/list.html",
    "/orders/update":               "/pages/orders/update.html",
    "/stocks":                      "/pages/stocks/index.html",
    "/stocks/receipt":              "/pages/stocks/receipt.html",
    "/stocks/history":              "/pages/stocks/history.html",
    "/picklists":                   "/pages/picklists/index.html",
    "/picklists/update":            "/pages/picklists/update.html",
    "/picklists/route":             "/pages/picklists/route.html",
    "/picklists/qr":                "/pages/picklists/qr.html",
    "/transfers":                   "/pages/transfers/index.html",
    "/transfers/list":              "/pages/transfers/list.html",
    "/reports":                     "/pages/reports/index.html",
    "/reports/reconciliation":      "/pages/reports/reconciliation.html",
    "/reports/daily":               "/pages/reports/daily.html",
    "/reports/weekly":              "/pages/reports/weekly.html",
    "/monitoring":                  "/pages/monitoring/index.html",
    "/monitoring/exceptions":       "/pages/monitoring/exceptions.html",
    "/monitoring/audit":            "/pages/monitoring/audit.html",
    "/monitoring/backorders":       "/pages/monitoring/backorders.html",
    "/monitoring/notifications":    "/pages/monitoring/notifications.html",
    "/upload":                      "/pages/upload/index.html",
}

import os

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        self.path = ROUTES.get(self.path, self.path)
        super().do_GET()

HTTPServer(("", 8080), Handler).serve_forever()
