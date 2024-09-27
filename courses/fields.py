from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)
    
    # it runs before the object is saved to the database
    def pre_save(self, model_instance, add):
        # checks if the object has current value if it is none the field is should automatically populated
        if getattr(model_instance, self.attname) is None:
        # no current value
            try:
                # retrive all the object of the model field is belong to 
                qs = self.model.objects.all()
                '''for_field is specified(eg.. group object by course)
                    it creates a filter based on the values of those fields
                    This means the new object will be ordered relative to other 
                    objects with the same for_fields values (like the same course or module).
                '''
                if self.for_fields:
                    # filter by objects with the same field values
                    # for the fields in "for_fields"
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    qs = qs.filter(**query)
                # get the order of the last item
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)