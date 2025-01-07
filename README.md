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

Make sure `settings.py` has the following:

```python
GAINSAY = {
  "url": 'redis://127.0.0.1:6379/0'
  "root": "gainsay"
}
```

`root` is the root key for all Gainsay events, and avoids collisions with other Redis keys.