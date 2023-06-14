# JSONField for MySQL Peewee library

This package is a JSONField on steroids for use with [ORM Peewee](https://github.com/coleifer/peewee), 
adding functions for working with NoSQL data (JSON fields)

By default, in Peewee, JSONField is a simple field inherited from TextField without any settings and additional methods, however, 
in MySQL/MariaDB there are [many methods](https://mariadb.com/kb/en/json-functions/) for working with JSON data that are either not used or 
need to be implemented yourself. This package is designed to fix this situation.

## Installation (in progress)
```pip install peeewee-jsonfield```

## Using

Suppose you have a table with a JSON type field, for example:

```
class TestModel(Model):
    id: int | AutoField = AutoField()
    data: dict | JSONField = JSONField()
```

With this library, you can use the SQL method `JSON_SET` using a simple python-specific syntax:
```
# Adding an integer variable to the "data" root
TestModel.data.jset('$.v_integer_key', 10).where(TestModel.id == 1).execute()
```
```
# Adding an dict variable to the "data" root
query: ModelUpdate = TestModel.data.jset('$.v_dict_key', {'nested1': 10})
query = query.where(TestModel.id == 1)
# ... any other where
query.execute()
```

You can use SQL method `JSON_MERGE_PATCH` to add nested variables in dict:
```
# Adding an nested dict variable to the root.v_dict_key
TestModel.data.jset('$.v_dict_key.nested_variable', 'nested_string').where(TestModel.id == 1).execute()

# Adding an nested list variable to the root.v_dict_key
TestModel.data.jset('$.v_dict_key.nested_list', [1, 2, 3]).where(TestModel.id == 1).execute()
```

Also, if you already have an object, instead of completely overwriting (`.save()`), you can use the `UPDATE` functions, specifying it as `target`
and `execute=True` if the request needs to be executed immediately:
```
obj: TestModel = TestModel.get(TestModel.id == 1)
# some reading code
TestModel.data.jset('$.v_integer_key', 30, target=obj, execute=True)
TestModel.data.jset('$.v_string_key', 'testing new library', target=obj, execute=True)
```

To remove fields from a JSON field, you can use the `.jremove()` method:
```
TestModel.data.jremove('$.v_integer_key', target=obj, execute=True)
TestModel.data.jremove('$.v_dict_key.nested1', target=obj, execute=True)

# Query without WHERE
TestModel.data.jremove('$.v_string_key', execute=True)
```

## Additional options
This field can also take additional options from the `dbhandle` object:
- `dbhandle.json_ensure_ascii = True` - setting the `ensure_ascii` parameter in the `json` library when saving data to the database
- `dbhandle.json_use_detailed = False` - setting the `indent=2` parameter in the `json` library and 
using the intermediate SQL formatting function `JSON_DETAILED` when saving data to the database

## More examples and try
View and run the file [jsonfield_play.py](https://github.com/mark99i/jsonfield/blob/master/jsonfield_play.py)

Before starting, you need to set environment variables to access the database: `db_name`, `db_port`, `db_passwd` 
and others (`db_host`, `db_port`, `opt_table_temporary`, `opt_json_ensure_ascii`, `opt_json_use_detailed`) as needed

## Limitations
This library is focused on working with MariaDB and MySQL DBMS and, most likely, will not work with others, since the syntax of SQL functions differs