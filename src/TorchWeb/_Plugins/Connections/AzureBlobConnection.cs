using Azure.Identity;
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Torch.Web.Collections;

namespace Torch.Web.Workflows.Connections;

public class AzureBlobConnection : Connection
{
    public AzureBlobConnection(int workflowId, string direction, string name = "Default Connection", string host = "torchhub")
        : base(workflowId, nameof(AzureBlobConnection), direction, name, host)
    {
        Client = new BlobServiceClient(new Uri($"https://{host}.blob.core.windows.net"), new DefaultAzureCredential());
        Container = Client.GetBlobContainerClient($"workflow-{workflowId}-{direction.ToLower()}");
    }

    public AzureBlobConnection(Workflow workflow, string direction, string name = "Default Connection", string host = "torchhub")
        : this(workflow.Id, direction, name, host)
    {
        Workflow = workflow;
    }

    private BlobServiceClient Client { get; }

    private BlobContainerClient Container { get; }

    internal override async Task<bool> InitializeAsync()
    {
        try
        {
            await Container.CreateIfNotExistsAsync();
            return true;
        }
        catch (Exception ex)
        {
            return false;
        }
    }

    internal override async Task<IEnumerable<Specimen>> GetSpecimensAsync(int take = 50, string? continuationToken = null)
    {
        var blobs = Container.GetBlobsAsync(BlobTraits.Metadata).AsPages(continuationToken, take);

        var specimens = new List<Specimen>();
        await foreach (var page in blobs)
        {
            foreach (var item in page.Values)
            {
                specimens.Add(new Specimen(Id, item.Metadata["Name"], item.Name));
            }
        }

        return specimens;
    }

    internal override async Task<Specimen> UploadSpecimenAsync(string fileName, Stream stream)
    {
        var name = Path.GetFileNameWithoutExtension(fileName);
        var blobName = $"{Guid.NewGuid()}{Path.GetExtension(fileName)}";
        
        var blob = Container.GetBlobClient(blobName);
        try
        {
            var result = await blob.UploadAsync(stream);
        }
        catch (Exception e)
        {
            Console.WriteLine(e);
        }

            var specimen = new Specimen(Id, name, blob.Name)
            {
                InputConnectionId = Id
            };
            Specimens.Add(specimen);
            return specimen;
    }
}
