from core.database import DB


class ModelSerializer:
    class Meta:
        model_class = None
        fields = None

    def __init__(self):

        self.meta = self.Meta()
        self._model_class = self.meta.model_class

        if not hasattr(self.meta, 'fields'):
            self._fields = None
        else:
            self._fields = self.meta.fields

        if not hasattr(self.meta, 'lookup_field'):
            self._lookup_field = None
        else:
            self._lookup_field = self.meta.lookup_field

    def get_queryset(self):
        model_class = self._model_class
        queryset = DB.session.query(model_class)
        return queryset

    def get_fields(self):
        return self._fields

    def get_lookup_field(self):
        return self._lookup_field

    def get_model_class(self):
        return self._model_class
