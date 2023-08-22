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
    }

    public AzureBlobConnection(Workflow workflow, string direction, string name = "Default Connection", string host = "torchhub")
        : this(workflow.Id, direction, name, host)
    {
        Workflow = workflow;
    }

    private string ContainerName => $"workflow-{WorkflowId}-{Direction.ToLower()}";

    private BlobServiceClient Client { get; }

    internal override async Task<bool> InitializeAsync()
    {
        try
        {
            var container = Client.GetBlobContainerClient(ContainerName);
            await container.CreateIfNotExistsAsync(PublicAccessType.Blob);
            return true;
        }
        catch (Exception ex)
        {
            return false;
        }
    }

    internal override async Task<IEnumerable<Specimen>> GetAsync(int take = 50, string? continuationToken = null)
    {
        var container = Client.GetBlobContainerClient(ContainerName);
        var blobs = container.GetBlobsAsync(BlobTraits.Metadata).AsPages(continuationToken, take);

        var specimens = new List<Specimen>();
        await foreach (var page in blobs)
        {
            foreach (var item in page.Values)
            {
                
                
                var batchId = item.Name.Split('/').First();
                var name = item.Name.Split('/').Last();
                var url = container.GetBlobClient(item.Name).Uri.ToString();

                var specimen = Specimens.FirstOrDefault(x => x.BatchId == batchId && x.InputFile == name)
                    ?? new Specimen(Id, batchId, item.Metadata.ContainsKey("Name") ? item.Metadata["Name"] : name, url);
                specimens.Add(specimen);
            }
        }

        return specimens;
    }

    internal override async Task<Specimen> UploadAsync(Specimen specimen, Stream stream)
    {
        var container = Client.GetBlobContainerClient(ContainerName);

        var name = Path.GetFileNameWithoutExtension(specimen.Name);
        var blobName = $"{specimen.BatchId}/{specimen.InputFile}";

        var blob = container.GetBlobClient(blobName);
        var result = await blob.UploadAsync(stream);
        specimen.SetInputFile(name, blob.Uri.ToString());
        Specimens.Add(specimen);
        return specimen;
    }
}
