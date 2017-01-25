from datetime import date


def populate_dict(fields, source):
    del source['_sa_instance_state']

    result_dict = dict()
    for key, value in source.items():
        if fields is None or key in fields:
            if isinstance(value, date):
                result_dict[key] = value.strftime("%Y-%m-%d")
            else:
                result_dict[key] = value
    return result_dict


class APIViewMixin:
    fields = None

    def response(self, source):
        return populate_dict(self.fields, source)


class ListAPIViewMixin:
    fields = None

    def response(self, source):
        return list(populate_dict(self.fields, row.__dict__) for row in source)
