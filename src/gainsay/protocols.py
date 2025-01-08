from typing import Protocol, Union, Any, List
import datetime

class GainsayProtocol(Protocol):
    def obj_table_id(self) -> str:
        ...
    
    def obj_id(self) -> Union[str,int]:
        ...

    def obj_pointer(self) -> Union[str,datetime.datetime]:
        ...

    def obj_channels(self) -> List[Union[str,int]]:
        ## optional
        ...

    ## note these is also obj_pointer_alias, but it is not required
    ## that is used for making Django queries more efficient
