

def del_response(main_schema, status_code: str):
    for path in main_schema['paths'].keys():
        for method in main_schema['paths'][path].keys():
            if '422' in main_schema['paths'][path][method]['responses']:
                del main_schema['paths'][path][method]['responses'][status_code]


def del_schema(main_schema, schema: str):
    if 'components' not in main_schema:
        return
    if 'schemas' not in main_schema['components']:
        return
    if schema in main_schema['components']['schemas']:
        del main_schema['components']['schemas'][schema]
