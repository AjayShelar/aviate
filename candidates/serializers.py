from rest_framework import serializers
from .models import Candidate

from django.core.validators import EmailValidator
from rest_framework import serializers


class CandidateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Candidate model with additional computed fields and validations.
    """
    age_category = serializers.SerializerMethodField(help_text="Categorizes age into Young, Mid-level, or Senior.")

    class Meta:
        model = Candidate
        fields = ['id', 'name', 'age', 'gender', 'email', 'phone_number', 'age_category']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True},
            'phone_number': {'required': True, 'min_length': 10, 'max_length': 15},
        }

    def get_age_category(self, obj):
        """
        Categorizes age into Young, Mid-level, or Senior.
        """
        if obj.age < 25:
            return "Young"
        elif 25 <= obj.age < 40:
            return "Mid-level"
        return "Senior"

    def validate_email(self, value):
        """
        Field-level validation for the email field.
        Ensures correct format and avoids forbidden content.
        """
        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except Exception:
            raise serializers.ValidationError("Enter a valid email address.")

        # Custom validation: forbid 'spam' in email addresses
        if "spam" in value.lower():
            raise serializers.ValidationError("Email cannot contain the word 'spam'.")
        
        return value

    def validate_age(self, value):
        """
        Field-level validation for age.
        """
        if value < 18:
            raise serializers.ValidationError("Age must be at least 18.")
        return value

    def validate_gender(self, value):
        """
        Field-level validation for gender.
        """
        if value not in ["M", "F", "O"]:
            raise serializers.ValidationError("Gender must be one of 'M', 'F', or 'O'.")
        return value

    def validate(self, data):
        """
        Object-level validation for cross-field constraints or global checks.
        """
        # If no cross-field validation is required, leave this method clean
        return data


class CandidateSearchSerializer(serializers.Serializer):
    """
    Serializer for validating query parameters for candidate search API.
    """
    q = serializers.CharField(
        max_length=255,
        required=True,
        help_text="Search query string. Maximum length is 255 characters.",
        error_messages={
            "required": "Search query is required.",
            "max_length": "Search query cannot exceed 255 characters.",
        },
    )
    page = serializers.IntegerField(
        min_value=1,
        required=False,
        default=1,
        help_text="Page number for pagination. Default is 1.",
    )
    page_size = serializers.IntegerField(
        min_value=1,
        max_value=100,
        required=False,
        default=10,
        help_text="Number of items per page. Default is 10. Maximum is 100.",
    )

    def validate_q(self, value):
        """
        Field-level validation for the query string.
        """
        if value.isdigit():
            raise serializers.ValidationError("Search query cannot be numeric.")
        return value

    def validate(self, data):
        """
        Object-level validation for pagination constraints or business rules.
        """
        page = data.get("page", 1)
        page_size = data.get("page_size", 10)

        # Example: Restrict maximum result limits
        if page * page_size > 10000:
            raise serializers.ValidationError(
                {"detail": "Pagination limits exceeded. Try reducing page size or page number."}
            )

        return data