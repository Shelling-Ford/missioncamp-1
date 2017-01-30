from flask_restful import fields


class DateField(fields.Raw):
    def format(self, value):
        return value.strftime("%Y-%m-%d")


class DateTimeField(fields.Raw):
    def format(self, value):
        return value.strftime("%Y-%m-%d %H:%M:%S")
