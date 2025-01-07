# Gainsay

Gainsay is a pub/sub event notification system for Object changes.

Producers - such as Django-derived Models - can define that they will _publish_ Gainsay events. 

Consumers _subscribe_ to events. 

Consumers can then _listen_ for events, which are delivered via callback. 
Using the PK and/or Timestamp provided in the event, only new events are delivered
as time progresses (even over reboots).

Consumers are responsible for actually getting the objects modified. 

You can _snoop_ on all events going through a LK system using

```bash
python manage.py gainsay_snoop
```

or to those being done to one "table" (basically but not always a Class) 

```bash
python manage.py gainsay_snoop --table-id applications.models.Application
```


## Configuration

### Dependencies

```requirements.txt
git+ssh://git@github.com/lenderkey/gainsay.git
```

```bash
pip install -r requirements.txt
```

### Django Settings

Make sure `settings.py` has the following:

```python
EVENT_SUPPRESS= False
GAINSAY = {
  "url": 'redis://127.0.0.1:6379/0'
  "root": "gainsay"
}
```

`root` is the root key for all Gainsay events, and avoids collisions with other Redis keys.

### Django Apps

Add the Gainsay App

```python
INSTALLED_APPS = [
    ...
    'gainsay',
    ...
]
```

Add database tables

```bash
python manage.py migrate gainsay
```

## Code

Add the following your models

```python
class MyModel(models.Model):
    last_updated: datetime.datetime = models.DateTimeField(default=timezone.now)

    @gainsay.publish_after
    @gainsay.update_timestamp("last_updated")
    def save(self, finalize:bool=True, *args, **kwargs):
        super().save(*args, **kwargs)

    ## the gainsay.EmitterProtocol
    def obj_table_id(self) -> str:
        return "myapp.models.MyModel"
    
    def obj_id(self) -> int:
        return self.pk

    def obj_pointer(self) -> str:
        from gainsay.utils import formatter_isodatetime
        return formatter_isodatetime(self.last_updated)
```

## Running

You can see events happening by running the snoop command

```bash
python manage.py gainsay_snoop
```