from wren import errors


class Collection(object):
    model = None

    def __init__(self, client):
        self.client = client

    def all(self):
        response = self.client.fetch(self.url)

        if response.status_code >= 400:
            response.raise_for_status()

        if hasattr(self, 'parse'):
            collection = self.parse(response)
        else:
            collection = escape.json_decode(response.body)

        if not isinstance(collection, list):
            raise ValueError("""
                The response body was expected to be a JSON array.

                To properly process the response you should define a
                `parse(raw)` method in your `Collection` class.""")

        result = []

        for r in collection:
            obj = self.model(**r)
            obj._persisted = True
            result.append(obj)

        return result

    # def get(self, id_, callback):
    #     def on_response(response):
    #         if response.code >= httplib.BAD_REQUEST:
    #             callback(None, errors.HTTPError(response.code))
    #             return

    #         result = self.model()

    #         if hasattr(result, 'parse'):
    #             resource = result.parse(response.body, response.headers)
    #         else:
    #             resource = escape.json_decode(response.body)

    #         try:
    #             result.update(resource)
    #         except Exception as error:
    #             callback(None, error)
    #         else:
    #             result._persisted = True
    #             callback(result, None)

    #     self.client.fetch(self._url(id_), callback=on_response)

    def _url(self, id_):
        url = getattr(self.model, '_url', self.url)

        if callable(url):
            return url(id_)

        url, query = splitquery(url)

        url = '{0}/{1}'.format(url, id_)

        if query is not None:
            url = '{0}?{1}'.format(url, query)

        return url

    # def add(self, obj, callback):
    #     def on_response(response):
    #         if response.code >= httplib.BAD_REQUEST:
    #             callback(None, errors.HTTPError(response.code))
    #             return

    #         if hasattr(obj, 'parse'):
    #             resource = obj.parse(response.body, response.headers)
    #         else:
    #             resource = escape.json_decode(response.body)

    #         try:
    #             obj.update(resource)
    #         except Exception as error:
    #             callback(None, error)
    #         else:
    #             obj._persisted = True
    #             callback(obj, None)

    #     if getattr(obj, '_persisted', False) is True:
    #         url = self._url(self._id(obj))
    #         method = 'PUT'
    #     else:
    #         url = self.url
    #         method = 'POST'

    #     if hasattr(obj, 'encode'):
    #         body, content_type = obj.encode()
    #     else:
    #         body, content_type = escape.json_encode(dict(obj)), 'application/json'

    #     self.client.fetch(url, method=method,
    #         headers={'Content-Type': content_type},
    #         body=body,
    #         callback=on_response)

    def _id(self, obj):
        for name, field in obj._fields.items():
            if field.options.get('primary', False):
                return getattr(obj, name)
