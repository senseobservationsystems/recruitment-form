from wtforms.widgets import TextInput


class DatePickerWidget(TextInput):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('class', 'dtpick')
        return super(DatePickerWidget, self).__call__(field, **kwargs)
