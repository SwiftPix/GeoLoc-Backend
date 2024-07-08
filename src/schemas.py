from marshmallow import Schema, fields


class CoordSchema(Schema):
    latitude = fields.Str(required=True, error_messages={"required": "A latitude é obrigatória"})
    longitude = fields.Str(required=True, error_messages={"required": "A longitude é obrigatória"})

class TaxSchema(CoordSchema):
    sender_currency = fields.Str(required=True, error_messages={"required": "A moeda desejada é obrigatória"})

class ConversionSchema(Schema):
    sender_currency = fields.Str(required=True, error_messages={"required": "A moeda base é obrigatória"})
    receiver_currency = fields.Str(required=True, error_messages={"required": "A moeda desejada é obrigatória"})
    value = fields.Float(required=True, error_messages={"required": "O valor a ser convertido é obrigatório"})

class ConversionCountrySchema(Schema):
    sender_country = fields.Str(required=True, error_messages={"required": "O país base é obrigatório"})
    receiver_country = fields.Str(required=True, error_messages={"required": "O país é obrigatório"})
    value = fields.Float(required=True, error_messages={"required": "O valor a ser convertido é obrigatório"})