import json

from peewee import TextField, Function, fn, ModelUpdate


class JSONField(TextField):
    field_type = 'JSON'

    def db_value(self, value):
        if value is not None:
            return json.dumps(value,
                              ensure_ascii=getattr(self.model._meta.database, 'json_ensure_ascii', True),
                              indent=2 if getattr(self.model._meta.database, 'json_use_detailed', False) else 0
                              )

    def python_value(self, value):
        if value is not None:
            return json.loads(value)

    def jextract(self, jpath: str) -> Function:
        # jpath example: '$.key1.key2'
        return fn.JSON_EXTRACT(self, jpath)

    # noinspection PyProtectedMember
    def jset(self, jpath: str, value: bool | int | str | dict | list | tuple, target = None, execute: bool = False) -> ModelUpdate | int:
        # jpath example: '$.key1.key2'

        if type(value) == tuple:
            value = list(value)

        if type(value) in [dict, list]:
            jset_q = self._jmerge(jpath, value)
        else:
            jset_q = fn.JSON_SET(self, jpath, value)

        if getattr(self.model._meta.database, 'json_use_detailed', False):
            jset_q = fn.JSON_DETAILED(jset_q)

        result = self.model.update(**{self.column_name: jset_q})

        if target:
            result = result.where(getattr(self.model, 'id') == target)

        if execute:
            result = result.execute()

        return result

    def _jmerge(self, jpath: str, value: dict | list) -> Function:
        keys = jpath[2:].split('.')
        result = { keys.pop(): value }
        while keys: result = { keys.pop(): result }
        result = json.dumps(result, ensure_ascii=getattr(self.model._meta.database, 'json_ensure_ascii', False))

        return fn.JSON_MERGE_PATCH(self, result)

    # noinspection PyProtectedMember
    def jremove(self, jpath: str, target = None, execute: bool = False) -> ModelUpdate | int:
        rm_q = fn.JSON_REMOVE(self, jpath)
        if getattr(self.model._meta.database, 'json_use_detailed', False):
            rm_q = fn.JSON_DETAILED(rm_q)

        result = self.model.update(**{self.column_name: rm_q})

        if target:
            result = result.where(getattr(self.model, 'id') == target)

        if execute:
            result = result.execute()

        return result