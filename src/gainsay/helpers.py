from typing import List, Iterable, Union
import datetime

from common.datetime import formatter_isodatetime

def obj_list(cls, field, 
    since:str=None, until:str=None, 
    limit:int=None, 
    cutoff:Union[datetime.datetime,str]=None,
    filters:List[str]=None,
    filterd:dict=None,
) -> Iterable:
    """
    This is a helper function to implement obj_list for Django models.
    """
    from common.datetime import advance_isodatetime

    if since:
        ## handle mismatch between milliseconds and database precision
        since = advance_isodatetime(since)

    if cutoff:
        cutoff = formatter_isodatetime(cutoff)
        
        if since:
            since = max(since, cutoff)
        else:
            since = cutoff

    filterd = dict(filterd or {})
    if since: filterd[f"{field}__gte"] = since
    if until: filterd[f"{field}__lte"] = until

    ## print("QUERY", cls, filterd)
    results = cls.objects.filter(**filterd).order_by(field)
    if limit:
        results = results[:limit]

    '''
    results = list(results)
    if results:
        print(results[0].when)

    if not filterd:
        import sys
        sys.exit(1)
    '''
    
    return results
