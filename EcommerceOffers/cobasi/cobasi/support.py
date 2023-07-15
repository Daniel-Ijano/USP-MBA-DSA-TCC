import json
from scrapy.http import Response

def get_data_json_response(
    response: Response, xpath: str = "//body/pre/text() | //div[@id='json']/text()"
):
    """
    Retrieve JSON data from a Response, via an XPath.

    Args:
        response (Response): Response from the Scrapy downloader
        xpath (str, optional): XPath selector containing the JSON string.
        Defaults to "//body/pre/text() | //div[@id='json']/text()".

    Returns:
        dict: JSON data from the Response, in dictionary form.
    """
    try:
        data = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        try:
            data = json.loads(response.xpath(xpath).get())
        except Exception:
            return {}
    except Exception:
        return {}

    return data


# def parse_date(date: str) -> str:
#     date_parsed = parse_dt(date, settings={"RETURN_AS_TIMEZONE_AWARE": False}) if date else None
#     return date_parsed.strftime("%Y-%m-%d %H:%M:%S") if date_parsed else None