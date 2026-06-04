from dataclasses import dataclass
from enum import Enum

HTTP_RETURN_CODES = {
    # Information response
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    # Success
    200: "Ok",
    201: "Created",
    202: "Accepted",
    203: "Non-Authorative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi Status",
    208: "Already Reported",
    226: "IM Used",
    # Redirection
    300: "Multiple Choices",
    301: "Moved Permenantly",
    302: "Found",
    303: "See other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Switch Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    # Client Error
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Content Too Large",
    414: "URI to Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Exception Failed",
    418: "I'm a teapot",  # joke type
    421: "Misdirected Request",
    422: "Unprocessable content",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition required",
    429: "Too many Requests",
    431: "Request Header fields to large",
    451: "Unavailable for legal reasons",
    # server errror
    500: "Internal Server Error",
    501: "Not implemented",
    502: "Bad Gateway",
    503: "Service unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version not supported",
    506: "Variant also negotiates",
    507: "Unsufficient storage",
    508: "Loop detected",
    510: "Not detected",
    511: "Network Authentication required",
    # Nonstandard codes
    440: "Login Time-out",
    449: "Retry With",
    450: "Blocked by Windows parental control",
    451: "Redirect",
    # nginx
    444: "No Response",
    494: "Request Header too Large",
    495: "SSL certificate Error",
    496: "SSL certificate Required",
    497: "Http request send to Https Port",
    499: "Client closed Request",
    # cloudflare
    520: "Web Server returned an unkown Error",
    521: "Web Server is down",
    522: "Connection Timed Out",
    523: "Origin is Unreachable",
    524: "A Timeout occured",
    525: "SSL Handshake Failed",
    526: "Invalid SSL Certificate",
    527: "Railgun Error",  # obsolete
    530: "Origin unavailable",
    # aws
    561: "Unauthorized",
}


@dataclass
class HttpStatusCode:
    coode: int
    msg: str

    def get_return_code(code: int) -> HttpStatusCode:
        if code in RETURN_CODES.keys():
            return HttpStatusCode(
                code,
                RETURN_CODES.get(code),
            )

        else:
            raise ValueError(f"No Return Code found for code {code}")

