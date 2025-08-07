from django import forms

from dentman.ops.models import Visit, Discount

class VisitDiscountForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = '__all__'

    def clean_discounts(self):
        discounts = self.cleaned_data['discounts']
        invalid_discounts = []

        for discount in discounts:
            if not discount.is_currently_valid:
                invalid_discounts.append(discount.name)

        if len(invalid_discounts) > 0:
            raise forms.ValidationError(f"These discounts are currently invalid: {", ".join(dis_name for dis_name in invalid_discounts)}")

        return discounts

class VisitAdminForm(VisitDiscountForm):
    pass
