from rich.console import Console
from rich.terminal_theme import NIGHT_OWLISH as THEME 
from zeep import Plugin
from lxml import etree
import datetime


class RichSoapDebugPlugin(Plugin):
    # timestamp of the last request
    last_request_timestamp = None

    def __init__(self, debug_console: Console = None):
        if debug_console is None:
            self.debug_console = Console(record=True)
        else:
            self.debug_console = debug_console

    def ingress(self, envelope, http_headers, operation):
        elapsed_time = datetime.datetime.now() - self.last_request_timestamp
        self.debug_console.print(f"Response ({elapsed_time}):")
        self.debug_console.print(etree.tostring(envelope, pretty_print=True).decode())

        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        self.last_request_timestamp = datetime.datetime.now()
        self.debug_console.print("Request:")
        self.debug_console.print(etree.tostring(envelope, pretty_print=True).decode())

        return envelope, http_headers

    def save_html(self, filename: str):
        self.debug_console.save_html(filename, theme=THEME)
