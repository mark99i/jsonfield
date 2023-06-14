import json
import os

from peewee import Model, AutoField, MySQLDatabase

from jsonfield.jsonfield import JSONField

dbhandle = MySQLDatabase(
    os.environ['db_name'],
    host=os.environ.get('db_host', 'localhost'),
    port=int(os.environ.get('db_port', 3306)),
    user=os.environ.get('db_user', 'root'),
    passwd=os.environ['db_passwd']
)

class TestModel(Model):
    id: int | AutoField = AutoField()
    data: dict | JSONField = JSONField()

    class Meta:
        database = dbhandle
        db_table = "test_table"
        order_by = ('id',)

def play():
    print('Connecting to memory db and create table')
    dbhandle.connect()
    dbhandle.create_tables([TestModel], temporary=os.environ.get('opt_table_temporary', True))

    # Optional variables for customization JSONField
    dbhandle.json_ensure_ascii = os.environ.get('opt_json_ensure_ascii', True)
    dbhandle.json_use_detailed = os.environ.get('opt_json_use_detailed', False)

    payload = {
        'v_int': 10,
        'v_str': 'my_body_string',
        'v_bool': True,
        'v_dict': {
            'v_in_dict': 20,
            'v_in_dict_dict': {
                'new_variable': 200
            }
        },
        'v_list': [
            'my_list_string1',
            'my_list_string2',
            'my_list_string3'
        ]
    }

    print('Inserting payload1 with ID = 1')
    TestModel.insert(id=1, data=payload).execute()
    payload2 = {}
    payload2 |= payload
    payload2['v_int'] = 20

    print('Inserting payload2 (v_int=20) with ID = 2')
    TestModel.insert(id=2, data=payload2).execute()

    print('Reading saved_payload from ID = 1:')
    saved_payload: TestModel = TestModel.get(TestModel.id == 1)
    print(json.dumps(saved_payload.data, indent=4), end='\n\n')

    print('Adding field with jset() and target=saved_payload')
    TestModel.data.jset('$.add_v_int', 100, target=saved_payload, execute=True)
    TestModel.data.jset('$.add_v_str', 'my_new_string', target=saved_payload, execute=True)
    TestModel.data.jset('$.add_v_bool', False, target=saved_payload, execute=True)
    TestModel.data.jset('$.add_v_list', [1, 2, 3], target=saved_payload, execute=True)
    TestModel.data.jset('$.add_v_dict', {'added': 'dict'}, target=saved_payload, execute=True)
    TestModel.data.jset('$.v_dict.add_nested_v_dict', {'added_nested': 'nested', 'added_nested1': 'remove_me'}, target=saved_payload, execute=True)

    print('Refresh saved_payload:')
    saved_payload = type(saved_payload).get_by_id(saved_payload.id)
    print(json.dumps(saved_payload.data, indent=4), end='\n\n')

    print('Removing old fields with jremove()')
    TestModel.data.jremove('$.v_str', target=saved_payload, execute=True)
    TestModel.data.jremove('$.v_bool', target=saved_payload, execute=True)
    TestModel.data.jremove('$.v_dict.v_in_dict', target=saved_payload, execute=True)
    TestModel.data.jremove('$.v_dict.v_in_dict_dict', target=saved_payload, execute=True)
    TestModel.data.jremove('$.v_dict.add_nested_v_dict.added_nested1', target=saved_payload, execute=True)
    TestModel.data.jremove('$.v_list', target=saved_payload, execute=True)

    print('Refresh saved_payload:')
    saved_payload = type(saved_payload).get_by_id(saved_payload.id)
    print(json.dumps(saved_payload.data, indent=4), end='\n\n')

    obj = TestModel.get_or_none(TestModel.data.jextract('$.v_int') == 10)
    print(f"Select by v_int = 10: ID {obj}")

    obj = TestModel.get_or_none(TestModel.data.jextract('$.v_int') == 20)
    print(f"Select by v_int = 20: ID {obj}")

    obj = TestModel.get_or_none(TestModel.data.jextract('$.add_v_str') == 'my_new_string')
    print(f"Select by add_v_str = my_new_string: ID {obj}")

    print('Playing with jremove()')
    TestModel.data.jremove('$.add_v_str').where(TestModel.data.jextract('$.add_v_str') == 'my_new_string').execute() # where manually by jextract
    TestModel.data.jremove('$.v_bool').where(TestModel.id == 2).execute()   # where manually by id
    TestModel.data.jremove('$.v_dict').execute()    # no where
    TestModel.data.jremove('$.v_int').execute()     # no where
    print()

    print('Result data from row ID = 1:')
    print(json.dumps(TestModel.get(TestModel.id == 1).data, indent=4))
    print('Result data from row ID = 2:')
    print(json.dumps(TestModel.get(TestModel.id == 2).data, indent=4))

if __name__ == "__main__":
    play()