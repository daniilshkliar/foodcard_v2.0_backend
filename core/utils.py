from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image as PILImage


def get_thumbnail(image, size=(300, 200)):
    """
    Creates a thumbnail of the specified SIZE from the passed base64 string.
    Returns an InMemoryUploadedFile object.
    """
    with PILImage.open(image) as img:
        img_io = BytesIO()
        img.thumbnail(size)
        img.save(img_io, img.format)
        image = InMemoryUploadedFile(
            img_io,
            None,
            str(image),
            image.content_type,
            len(img_io.getvalue()),
            None
        )
        return image