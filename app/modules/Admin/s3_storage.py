import os
import io
from flask import current_app
from minio.error import S3Error
from app.extensions import seraphina  # Import Seraphina from extensions


class S3Storage:
    """Static class to manage MinIO S3 storage operations with Seraphina logging."""

    @staticmethod
    def get_client():
        """Retrieve the MinIO client from Flask extensions."""
        client = current_app.extensions.get("minio_client")
        if not client:
            seraphina.error("🔴 MinIO client is not initialized!")
        return client

    @staticmethod
    def upload_file(bucket_name, object_name, file_data, content_type="application/octet-stream"):
        """
        Uploads a file to MinIO.

        :param bucket_name: Name of the bucket.
        :param object_name: Path where the file should be stored (e.g., 'store/product/1/image.jpg').
        :param file_data: File data (bytes or file object).
        :param content_type: MIME type of the file.
        :return: URL of the uploaded file or error message.
        """
        try:
            client = S3Storage.get_client()
            if not client:
                return {"error": "MinIO client not initialized"}

            # Ensure the bucket exists
            if not client.bucket_exists(bucket_name):
                seraphina.info(f"📦 Bucket '{bucket_name}' not found. Creating it now...")
                client.make_bucket(bucket_name)

            # Convert file_data to bytes (if it's a file object)
            if not isinstance(file_data, bytes):
                file_data = file_data.read()

            # Upload file
            client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )

            # Generate file URL
            file_url = f"https://{client._endpoint}/{bucket_name}/{object_name}"
            seraphina.success(f"📤 File uploaded successfully: {file_url}")
            return {"success": True, "url": file_url}

        except S3Error as e:
            seraphina.error(f"❌ MinIO error: {str(e)}")
            return {"error": f"MinIO error: {str(e)}"}
        except Exception as e:
            seraphina.critical(f"🔥 Unexpected error during upload: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def delete_file(bucket_name, object_name):
        """
        Deletes a file from MinIO.

        :param bucket_name: Name of the bucket.
        :param object_name: Path of the file to delete.
        :return: Success or error message.
        """
        try:
            client = S3Storage.get_client()
            if not client:
                return {"error": "MinIO client not initialized"}

            client.remove_object(bucket_name, object_name)
            seraphina.success(f"🗑️ Deleted {object_name} from {bucket_name}")
            return {"success": True, "message": f"Deleted {object_name} from {bucket_name}"}

        except S3Error as e:
            seraphina.error(f"❌ MinIO error: {str(e)}")
            return {"error": f"MinIO error: {str(e)}"}
        except Exception as e:
            seraphina.critical(f"🔥 Unexpected error during deletion: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def get_presigned_url(bucket_name, object_name, expires_in=3600):
        """
        Generates a pre-signed URL for accessing a file.

        :param bucket_name: Name of the bucket.
        :param object_name: Path of the file.
        :param expires_in: Expiry time in seconds (default: 1 hour).
        :return: Pre-signed URL or error message.
        """
        try:
            client = S3Storage.get_client()
            if not client:
                return {"error": "MinIO client not initialized"}

            presigned_url = client.presigned_get_object(bucket_name, object_name, expires=expires_in)
            seraphina.info(f"🔗 Generated pre-signed URL for {object_name} (expires in {expires_in}s)")
            return {"success": True, "url": presigned_url}

        except S3Error as e:
            seraphina.error(f"❌ MinIO error: {str(e)}")
            return {"error": f"MinIO error: {str(e)}"}
        except Exception as e:
            seraphina.critical(f"🔥 Unexpected error during URL generation: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    @staticmethod
    def list_files(bucket_name, prefix=""):
        """
        Lists all files in a given bucket.

        :param bucket_name: Name of the bucket.
        :param prefix: Prefix for filtering files (optional).
        :return: List of file names or error message.
        """
        try:
            client = S3Storage.get_client()
            if not client:
                return {"error": "MinIO client not initialized"}

            objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
            file_list = [obj.object_name for obj in objects]

            seraphina.info(f"📜 Listed {len(file_list)} files in '{bucket_name}'")
            return {"success": True, "files": file_list}

        except S3Error as e:
            seraphina.error(f"❌ MinIO error: {str(e)}")
            return {"error": f"MinIO error: {str(e)}"}
        except Exception as e:
            seraphina.critical(f"🔥 Unexpected error during listing: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
