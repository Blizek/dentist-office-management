import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from dentman.ops.models import Post

# --- FIXTURES ---

@pytest.fixture
def image_file():
    """Creates a dummy image file for testing."""
    return SimpleUploadedFile(
        "test_image.jpg",
        b"binary_content_of_image",
        content_type="image/jpeg"
    )

@pytest.fixture
def post(db, image_file):
    """Creates a basic Post instance."""
    return Post.objects.create(
        title="First Post",
        slug="first-post",
        text_html="<p>Hello World</p>",
        main_photo=image_file
    )

# --- TESTS ---

@pytest.mark.django_db
def test_post_creation_happy_path(post):
    """
    Test creating a valid post.
    Checks basic fields and string representation.
    """
    assert post.title == "First Post"
    assert post.slug == "first-post"
    assert post.visit_counter == 0
    assert "test_image" in post.main_photo.name
    assert str(post) == "Post First Post"


@pytest.mark.django_db
def test_post_title_uniqueness(post):
    """
    Test that post title must be unique.
    FullCleanMixin should raise ValidationError.
    """
    duplicate_post = Post(
        title="First Post",  # Same title
        slug="unique-slug",
        text_html="Content"
    )

    with pytest.raises(ValidationError) as excinfo:
        duplicate_post.save()
    
    assert "title" in excinfo.value.message_dict
    assert "already exists" in str(excinfo.value.message_dict["title"])


@pytest.mark.django_db
def test_post_slug_uniqueness(post):
    """
    Test that post slug must be unique.
    """
    duplicate_post = Post(
        title="Unique Title",
        slug="first-post",  # Same slug
        text_html="Content"
    )

    with pytest.raises(ValidationError) as excinfo:
        duplicate_post.save()
    
    assert "slug" in excinfo.value.message_dict


@pytest.mark.django_db
def test_post_save_without_image_change(post):
    """
    Test that 'delete_old_file' is NOT called if we save but don't change the photo.
    """
    with patch("dentman.man.models.delete_old_file") as mock_delete:
        
        post.title = "Updated Title"
        post.save()
        
        # Should not be called because photo didn't change
        assert mock_delete.called is False


@pytest.mark.django_db
def test_post_html_content_storage(image_file):
    """
    Test if HTML content is stored correctly (sanity check for HTMLField).
    """
    html_content = "<div class='content'><h1>Header</h1></div>"
    post = Post.objects.create(
        title="HTML Test",
        slug="html-test",
        text_html=html_content,
        main_photo=image_file
    )
    
    assert post.text_html == html_content