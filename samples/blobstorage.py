from azure.storage.blob import BlockBlobService

if __name__ == "__main__":
    # init logging
    #initLogging()

    # instantiate the client
    blobService = BlockBlobService(account_name='blobname', account_key='insertkey')

    # list all blobs in a container
    container = blobService.list_blobs('public')
    for blob in container:
        print("Blob found: " + blob.name)
    
    # get a blob
    blobService.get_blob_to_path('public', 'testimage.PNG', 'out-image.png')
    print("Blob downloaded as out-image.png")