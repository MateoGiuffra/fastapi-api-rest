import inspect
def get_json(instance_object):
    methods = inspect.getmembers(instance_object, predicate=inspect.ismethod)
    result = {}   
    for name_method, method in methods: 
        if name_method.startswith("__"): continue
        signature = inspect.signature(method)
        params = list(signature.parameters.values())
        if len(params) == 2: # Los manejadores de excepción tienen 2 parámetros (request, exc)
            result[params[1].annotation] = method
    return result