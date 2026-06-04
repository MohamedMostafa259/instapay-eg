# Django Integration

Install: `pip install "instapay-eg[django]"`

## ORM Model Field

`InstaPayLinkField` is a `CharField` subclass. On `full_clean()` / `save()`, it automatically extracts and security-checks the InstaPay link:

```python
from django.db import models
from instapay_eg.integrations.django import InstaPayLinkField

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    instapay_link = InstaPayLinkField(blank=True, null=True)
    # ^ Automatically validates and stores only the clean URL
```

Migration:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Form Field

Use `InstaPayHandleFormField` in Django forms or `ModelForm`:

```python
from django import forms
from instapay_eg.integrations.django import InstaPayHandleFormField

class PaymentForm(forms.Form):
    recipient = InstaPayHandleFormField(
        label="InstaPay Handle",
        help_text="Enter the recipient's @instapay handle.",
    )
```

The field accepts `alice` or `alice@instapay` - the suffix is stripped before validation.

## Admin Integration

`InstaPayLinkField` works in Django Admin with zero extra configuration:

```python
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "instapay_link"]
    search_fields = ["instapay_link"]
```
