# (Bonus) Lab Week 09: Google Cloud Storage (GCS)

This is just a quick example lab to show [Google Cloud Storage](https://cloud.google.com/storage/docs/introduction), what it can do and how it can be used.

Google Cloud Storage (GCS) is a highly durable and highly available object storage service offered by Google Cloud.

It is usually used to store and access any amount of data from anywhere in the world.

It is included in this course as it is a convenient way to **stage data so it is available by different services in the Cloud**.

:point_right: For example, you built a **dashboard** that should access **data** produced by another service (or model), then you can use GCS for that. Note that there are better suited services such as [BigQuery](https://cloud.google.com/bigquery/docs) for that but let's keep it simple here.

## 0. Setup

Make sure to have a GCP project you can use
1. Visit the [Google Cloud Console](https://console.cloud.google.com/) and either select a project or create a new one.
2. :sunglasses: Note that you can give access to other users to your GCP project through the [IAM page](https://console.cloud.google.com/iam-admin/) - so multiple project can work on one project **with the same billing account**
3. Make sure to have a [billing account](https://console.cloud.google.com/billing/) (remember that you can request credits to the teaching staff!)

Enable the Cloud Storage API:
1. Navigate to the [Cloud storage tab](https://console.cloud.google.com/storage)
2. If requested Enable the API

And we will then **create a bucket** in which we will store the files for this lab.

You can do so from the UI directly.

We will then create a Service Account key to be used locally.

1. Go to the [service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) tab in the IAM & Admin page
2. Click "create service account"
   1. Give it a name and description (e.g. `gcs-access`)
   2. In "Grant this service account access to project". Go to the `Select a role` drop-down list, in `By product or service` choose `Cloud Storage` and give it the `Storage Object Admin` role.
   3. Once created, click on the service account and go to the `KEYS` tab
   4. Click on `ADD KEY` and select JSON. That will download a service account key locally which has access to GCS :smiley:
   5. Save that JSON file locally and **make sure to not upload it to git!**


## 1. Using the python SDK to upload files

Create a jupyter notebook (e.g. `cloud_storage.ipynb`) and do the following:

First, install the Google Cloud Storage Python client library:

```sh
!pip install google-cloud-storage
```

Then, we set your Google Cloud credentials as a global variable by pointing to the local service account key (replace with {svc_key_location} with your actual local service account JSON path):

```sh
!export GOOGLE_APPLICATION_CREDENTIALS={svc_key_location}
```

We will now upload a local file by running the following code in a new cell:

```python
from google.cloud import storage

def upload_blob(service_account_path, bucket_name, source_file_path, destination_blob_name):
    """Uploads a file to the specified bucket."""
    storage_client = storage.Client.from_service_account_json(service_account_path)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    print(f"File {source_file_path} uploaded to {destination_blob_name}.")

# Set variables
service_account_path = '{your_svc_path}'
bucket_name = 'mlsd-bucket-2'
source_file_path = 'data/housing.csv'
destination_blob_name = 'housing.csv'

# Example usage
upload_blob(service_account_path, bucket_name, source_file_path, destination_blob_name)
```

And we can even download that file back locally by running this in another cell:

```python
def download_blob(service_account_path, bucket_name, gcs_blob_path, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client.from_service_account_json(service_account_path)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_path)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {gcs_blob_path} downloaded to {destination_file_name}.")

# Set variables
service_account_path = '{your_svc_path}'
bucket_name = 'mlsd-bucket-2'
gcs_blob_path = 'housing.csv'
destination_file_name = 'data/housing_downloaded.csv'

# Example usage
download_blob(service_account_path, bucket_name, gcs_blob_path, destination_file_name)
```

:muscle: That's it, we managed to upload and download files from GCS !

It is a small thing but it shows you how this can be used to let services access data from the Cloud.

If you want to access structured (or relational) data in a cleaner way check out [BigQuery](https://cloud.google.com/bigquery/docs).