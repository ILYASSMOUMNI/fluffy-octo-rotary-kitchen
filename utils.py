import cloudinary.uploader
from django.core.files.uploadedfile import InMemoryUploadedFile
from typing import Optional

def upload_image(
    image: InMemoryUploadedFile,
    folder: str = 'default',
    public_id: Optional[str] = None,
    transformation: Optional[dict] = None
) -> dict:
    """
    Upload an image to Cloudinary.
    
    Args:
        image: The image file to upload
        folder: The folder in Cloudinary where the image will be stored
        public_id: Optional custom public ID for the image
        transformation: Optional transformation parameters
        
    Returns:
        dict: Cloudinary upload response
    """
    try:
        upload_options = {
            'folder': folder,
        }
        
        if public_id:
            upload_options['public_id'] = public_id
            
        if transformation:
            upload_options['transformation'] = transformation
            
        result = cloudinary.uploader.upload(
            image,
            **upload_options
        )
        return result
    except Exception as e:
        raise Exception(f"Error uploading image to Cloudinary: {str(e)}")

def delete_image(public_id: str) -> dict:
    """
    Delete an image from Cloudinary.
    
    Args:
        public_id: The public ID of the image to delete
        
    Returns:
        dict: Cloudinary delete response
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        raise Exception(f"Error deleting image from Cloudinary: {str(e)}") 